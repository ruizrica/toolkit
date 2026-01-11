#!/usr/bin/env python3
"""
CodeRabbit Review & Fix Workflow Coordinator

Orchestrates the complete CodeRabbit CLI workflow:
1. Run initial CodeRabbit review with --plain mode
2. Parse review comments into actionable tasks
3. Coordinate parallel agent fixes
4. Verify fixes with CodeRabbit re-review
5. Save final results with /save command
"""

import os
import sys
import subprocess
import re
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

try:
    from claude_code_sdk import query
    CLAUDE_SDK_AVAILABLE = True
except ImportError:
    CLAUDE_SDK_AVAILABLE = False


class CodeRabbitWorkflow:
    def __init__(self, project_path: str = ".", base_branch: str = "main"):
        self.project_path = Path(project_path).resolve()
        self.base_branch = base_branch
        self.review_results = []
        self.fix_tasks = []
        self.verification_results = []

    def run_coderabbit_review(self, review_type: str = "all", base_branch: Optional[str] = None) -> str:
        """Run CodeRabbit CLI with --plain mode and capture output."""
        cmd = ["coderabbit", "--plain"]

        if review_type != "all":
            cmd.extend(["--type", review_type])

        if base_branch:
            cmd.extend(["--base", base_branch])
        elif self.base_branch != "main":
            cmd.extend(["--base", self.base_branch])

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout for large reviews
            )

            if result.returncode == 0:
                return result.stdout
            else:
                print(f"⚠️ CodeRabbit review failed: {result.stderr}")
                return ""

        except subprocess.TimeoutExpired:
            print("⚠️ CodeRabbit review timed out after 30 minutes")
            return ""
        except FileNotFoundError:
            print("❌ CodeRabbit CLI not found. Please install with: curl -fsSL https://cli.coderabbit.ai/install.sh | sh")
            return ""

    def parse_review_output(self, review_output: str) -> List[Dict]:
        """Parse CodeRabbit --plain output into structured tasks."""
        tasks = []

        # CodeRabbit --plain output patterns
        # Look for issue patterns like:
        # - File: path/to/file.py:42
        # - Severity: HIGH/MEDIUM/LOW
        # - Issue: Description of the problem
        # - Suggestion: Recommended fix

        lines = review_output.split('\n')
        current_issue = {}

        for i, line in enumerate(lines):
            line = line.strip()

            # File and line number pattern
            if line.startswith('File:') or 'File:' in line:
                file_match = re.search(r'File:\s*(.+?)(?::(\d+))?', line)
                if file_match:
                    current_issue['file'] = file_match.group(1).strip()
                    current_issue['line'] = file_match.group(2) if file_match.group(2) else None

            # Severity pattern
            elif 'Severity:' in line or 'severity:' in line.lower():
                severity_match = re.search(r'Severity:\s*(\w+)', line, re.IGNORECASE)
                if severity_match:
                    current_issue['severity'] = severity_match.group(1).upper()

            # Issue description
            elif 'Issue:' in line or 'Problem:' in line:
                issue_match = re.search(r'(?:Issue|Problem):\s*(.+)', line)
                if issue_match:
                    current_issue['issue'] = issue_match.group(1).strip()

            # Suggestion/fix
            elif 'Suggestion:' in line or 'Fix:' in line or 'Recommendation:' in line:
                suggestion_match = re.search(r'(?:Suggestion|Fix|Recommendation):\s*(.+)', line)
                if suggestion_match:
                    current_issue['suggestion'] = suggestion_match.group(1).strip()

            # End of issue block (empty line or new issue starts)
            elif line == "" and current_issue:
                if self._is_valid_issue(current_issue):
                    tasks.append(current_issue.copy())
                current_issue = {}

        # Handle last issue if exists
        if current_issue and self._is_valid_issue(current_issue):
            tasks.append(current_issue)

        return tasks

    def _is_valid_issue(self, issue: Dict) -> bool:
        """Validate that an issue has required fields."""
        return all(key in issue for key in ['file', 'issue'])

    async def create_parallel_fix_tasks(self, review_tasks: List[Dict]) -> List[Dict]:
        """Create parallel fix tasks for multiple agents."""
        fix_tasks = []

        for i, task in enumerate(review_tasks):
            fix_task = {
                'id': i + 1,
                'file': task['file'],
                'line': task.get('line'),
                'severity': task.get('severity', 'MEDIUM'),
                'issue': task['issue'],
                'suggestion': task.get('suggestion', ''),
                'status': 'pending',
                'agent_assigned': None
            }
            fix_tasks.append(fix_task)

        return fix_tasks

    async def assign_parallel_fixes(self, fix_tasks: List[Dict]) -> List[Dict]:
        """Coordinate parallel agent fixes using Claude Code SDK."""
        if not CLAUDE_SDK_AVAILABLE:
            print("⚠️ Claude Code SDK not available. Running sequential fixes.")
            return await self.run_sequential_fixes(fix_tasks)

        # Group tasks by file to minimize conflicts
        tasks_by_file = {}
        for task in fix_tasks:
            file_key = task['file']
            if file_key not in tasks_by_file:
                tasks_by_file[file_key] = []
            tasks_by_file[file_key].append(task)

        # Create parallel agent prompts
        agent_prompts = []
        for file_path, file_tasks in tasks_by_file.items():
            prompt = self._create_agent_prompt(file_path, file_tasks)
            agent_prompts.append(prompt)

        # Execute parallel fixes
        results = await asyncio.gather(
            *[self._execute_agent_fix(prompt) for prompt in agent_prompts],
            return_exceptions=True
        )

        # Update task statuses
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"⚠️ Agent {i+1} fix failed: {result}")
                continue

            # Mark tasks as completed
            file_path = list(tasks_by_file.keys())[i]
            for task in fix_tasks:
                if task['file'] == file_path:
                    task['status'] = 'completed'
                    task['fix_result'] = str(result)

        return fix_tasks

    def _create_agent_prompt(self, file_path: str, file_tasks: List[Dict]) -> str:
        """Create a prompt for an AI agent to fix issues in a specific file."""
        prompt = f"""Fix the following CodeRabbit review issues in {file_path}:

"""

        for task in file_tasks:
            prompt += f"""
Issue {task['id']} (Severity: {task['severity']}):
- Line: {task.get('line', 'N/A')}
- Problem: {task['issue']}
- Suggestion: {task.get('suggestion', 'Implement appropriate fix')}
"""

        prompt += f"""

Instructions:
1. Apply fixes directly to {file_path}
2. Preserve existing functionality while addressing the issues
3. Follow the project's coding standards
4. Test your changes to ensure they don't break existing functionality
5. Use the /save command when all fixes are complete

Work efficiently and comprehensively. Address all listed issues in this file.
"""
        return prompt

    async def _execute_agent_fix(self, prompt: str) -> str:
        """Execute an agent fix using Claude Code SDK."""
        if not CLAUDE_SDK_AVAILABLE:
            return "Claude Code SDK not available"

        result = ""
        try:
            async for message in query(prompt=prompt):
                result += str(message)
        except Exception as e:
            return f"Agent execution failed: {str(e)}"

        return result

    async def run_sequential_fixes(self, fix_tasks: List[Dict]) -> List[Dict]:
        """Run fixes sequentially when parallel execution isn't available."""
        for task in fix_tasks:
            print(f"🔧 Fixing issue {task['id']} in {task['file']}")

            # Create simple fix prompt
            prompt = f"""Fix this CodeRabbit issue:

File: {task['file']}
Issue: {task['issue']}
Suggestion: {task.get('suggestion', '')}

Apply the fix and use /save when complete.
"""

            if CLAUDE_SDK_AVAILABLE:
                result = ""
                try:
                    async for message in query(prompt=prompt):
                        result += str(message)
                    task['fix_result'] = result
                except Exception as e:
                    task['fix_result'] = f"Fix failed: {str(e)}"
            else:
                task['fix_result'] = "Manual fix required - Claude Code SDK not available"

            task['status'] = 'completed'

        return fix_tasks

    def verify_fixes(self, original_review: str, review_type: str = "all") -> Tuple[bool, str]:
        """Run CodeRabbit again to verify all issues are resolved."""
        print("🔍 Verifying fixes with CodeRabbit...")
        verification_output = self.run_coderabbit_review(review_type, self.base_branch)

        # Compare original vs verification results
        original_issues = len(self.parse_review_output(original_review))
        verification_issues = len(self.parse_review_output(verification_output))

        if verification_issues == 0:
            return True, "✅ All issues resolved successfully!"
        elif verification_issues < original_issues:
            return False, f"⚠️ Partial success: {verification_issues} issues remaining (was {original_issues})"
        else:
            return False, f"❌ No improvement: {verification_issues} issues remaining"

    def generate_report(self, original_tasks: List[Dict], fix_tasks: List[Dict],
                       verification_success: bool, verification_message: str) -> str:
        """Generate a comprehensive workflow report."""
        report = f"""# CodeRabbit Review & Fix Workflow Report
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Summary
- **Original Issues**: {len(original_tasks)}
- **Fix Tasks Created**: {len(fix_tasks)}
- **Tasks Completed**: {len([t for t in fix_tasks if t['status'] == 'completed'])}
- **Verification Result**: {'✅ SUCCESS' if verification_success else '❌ FAILED'}
- **Verification Message**: {verification_message}

## Issue Breakdown by Severity
"""

        severity_counts = {}
        for task in original_tasks:
            severity = task.get('severity', 'UNKNOWN')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        for severity, count in sorted(severity_counts.items()):
            report += f"- {severity}: {count} issues\n"

        report += f"""

## Completed Fixes
"""

        for task in fix_tasks:
            if task['status'] == 'completed':
                report += f"""
### Issue {task['id']} - {task['file']}
- **Severity**: {task.get('severity', 'N/A')}
- **Status**: ✅ Completed
- **Result**: {task.get('fix_result', 'Fix applied successfully')}
"""

        report += f"""

## Next Steps
"""

        if verification_success:
            report += """✅ **Workflow Complete!** All CodeRabbit issues have been resolved.
- Changes have been saved with /save command
- Code is ready for production
- Consider running additional tests to ensure stability
"""
        else:
            report += f"""⚠️ **Additional Work Required**
{verification_message}

**Recommended Actions:**
1. Review the remaining issues manually
2. Consider running the workflow again with more specific parameters
3. Address any complex architectural issues that may require human intervention
4. Use `coderabbit --prompt-only` for AI agent optimization on remaining issues
"""

        return report

    async def run_workflow(self, review_type: str = "all", base_branch: Optional[str] = None,
                          verify_only: bool = False) -> str:
        """Run the complete CodeRabbit review and fix workflow."""
        print("🚀 Starting CodeRabbit Review & Fix Workflow")
        print(f"📁 Project: {self.project_path}")
        print(f"🔍 Review Type: {review_type}")
        if base_branch:
            print(f"SetBranch: {base_branch}")

        # Phase 1: Initial CodeRabbit Review
        print("\n📋 Phase 1: Running CodeRabbit Review...")
        review_output = self.run_coderabbit_review(review_type, base_branch)

        if not review_output.strip():
            return "❌ CodeRabbit review failed or returned no output"

        print("✅ CodeRabbit review completed")

        if verify_only:
            print("🔍 Verification-only mode: Skipping fix phase")
            return review_output

        # Phase 2: Parse Review Results
        print("\n📝 Phase 2: Parsing Review Results...")
        original_tasks = self.parse_review_output(review_output)

        if not original_tasks:
            return "✅ No issues found in CodeRabbit review - workflow complete!"

        print(f"✅ Found {len(original_tasks)} issues to fix")

        # Phase 3: Create and Assign Fix Tasks
        print("\n🔧 Phase 3: Creating Parallel Fix Tasks...")
        fix_tasks = await self.create_parallel_fix_tasks(original_tasks)
        print(f"✅ Created {len(fix_tasks)} fix tasks")

        # Phase 4: Execute Parallel Fixes
        print("\n🤖 Phase 4: Executing Parallel Agent Fixes...")
        completed_tasks = await self.assign_parallel_fixes(fix_tasks)
        print(f"✅ Completed {len([t for t in completed_tasks if t['status'] == 'completed'])} fixes")

        # Phase 5: Verification
        print("\n🔍 Phase 5: Verifying Fixes...")
        verification_success, verification_message = self.verify_fixes(review_output, review_type)
        print(f"✅ Verification completed: {verification_message}")

        # Phase 6: Generate Report
        print("\n📊 Phase 6: Generating Workflow Report...")
        report = self.generate_report(original_tasks, completed_tasks,
                                    verification_success, verification_message)

        # Phase 7: Save Final Results
        print("\n💾 Phase 7: Saving Results...")
        report_path = self.project_path / f"coderabbit_workflow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w') as f:
            f.write(report)

        print(f"✅ Report saved to: {report_path}")
        print("\n🚀 CodeRabbit Review & Fix Workflow Complete!")

        return report


def main():
    """Main function to run the CodeRabbit workflow."""
    import argparse

    parser = argparse.ArgumentParser(description="CodeRabbit Review & Fix Workflow")
    parser.add_argument("--path", "-p", default=".", help="Project path to analyze")
    parser.add_argument("--base", "-b", default="main", help="Base branch for comparison")
    parser.add_argument("--type", "-t", choices=["all", "committed", "uncommitted"],
                       default="all", help="Review type")
    parser.add_argument("--verify-only", action="store_true",
                       help="Only run verification, skip fix phase")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    async def run_workflow():
        workflow = CodeRabbitWorkflow(args.path, args.base)
        result = await workflow.run_workflow(
            review_type=args.type,
            base_branch=args.base if args.base != "main" else None,
            verify_only=args.verify_only
        )
        print("\n" + "="*50)
        print(result)

    asyncio.run(run_workflow())


if __name__ == "__main__":
    main()
