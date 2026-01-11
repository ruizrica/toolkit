#!/usr/bin/env python3

# ABOUTME: Handbook Generator - Creates comprehensive project documentation
# ABOUTME: Analyzes codebase structure and generates AI-optimized navigation handbooks
# 
# OAuth Token Authentication:
# - Set CLAUDE_CODE_OAUTH_TOKEN or HANDBOOK_CLAUDE_OAUTH_TOKEN environment variable
# - Or use --oauth-token command line argument
# - Uses Claude Agent SDK with Max Plan authentication (no API costs)

import os
import json
import subprocess
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple
import re

try:
    from claude_agent_sdk import query as sdk_query, AssistantMessage, ResultMessage
    from claude_agent_sdk.types import TextBlock
    CLAUDE_SDK_AVAILABLE = True
except ImportError:
    CLAUDE_SDK_AVAILABLE = False
    print("⚠️  Claude Agent SDK not available. Install with: pip install claude-agent-sdk")


class HandbookGenerator:
    """
    Generates comprehensive project handbooks for AI-optimized navigation.

    This tool analyzes project structure, detects technologies, and creates
    a 4-layer handbook following standard practices.
    """

    def __init__(self, project_path: str = ".", enable_ai_analysis: bool = True):
        self.project_path = Path(project_path).resolve()
        if not CLAUDE_SDK_AVAILABLE:
            raise ImportError("Claude Agent SDK is required. Install with: pip install claude-agent-sdk")
        self.enable_ai_analysis = enable_ai_analysis
        self.languages = set()
        self.frameworks = set()
        self.build_tools = set()
        self.test_frameworks = set()
        self.config_files = []
        self.modules = []
        self.apis = []
        self.ai_insights = {}

    def detect_languages(self) -> Set[str]:
        """Detect programming languages used in the project."""
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript (JSX)',
            '.tsx': 'TypeScript (TSX)',
            '.java': 'Java',
            '.kt': 'Kotlin',
            '.swift': 'Swift',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.scala': 'Scala',
            '.clj': 'Clojure',
            '.dart': 'Dart',
            '.r': 'R',
            '.sql': 'SQL',
            '.sh': 'Shell Script',
            '.ps1': 'PowerShell',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'SASS',
            '.less': 'LESS'
        }

        for root, dirs, files in os.walk(self.project_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', '.pytest_cache', 'venv', 'env', 'build', 'dist', 'target'}]

            for file in files:
                ext = Path(file).suffix.lower()
                if ext in language_extensions:
                    self.languages.add(language_extensions[ext])

        return self.languages

    def detect_frameworks_and_tools(self) -> Tuple[Set[str], Set[str], Set[str]]:
        """Detect frameworks, build tools, and test frameworks."""
        # Check for common configuration files
        config_indicators = {
            'package.json': self._analyze_package_json,
            'requirements.txt': self._analyze_requirements_txt,
            'pom.xml': self._analyze_pom_xml,
            'build.gradle': self._analyze_gradle,
            'Cargo.toml': self._analyze_cargo_toml,
            'go.mod': self._analyze_go_mod,
            'composer.json': self._analyze_composer_json,
            'Gemfile': self._analyze_gemfile,
            'pubspec.yaml': self._analyze_pubspec,
            'pyproject.toml': self._analyze_pyproject_toml
        }

        for config_file, analyzer in config_indicators.items():
            config_path = self.project_path / config_file
            if config_path.exists():
                self.config_files.append(str(config_path.relative_to(self.project_path)))
                analyzer(config_path)

        # Check for framework-specific files
        self._detect_framework_files()

        return self.frameworks, self.build_tools, self.test_frameworks

    def _analyze_package_json(self, path: Path):
        """Analyze package.json for JavaScript/TypeScript projects."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)

            dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}

            # Frameworks
            if 'react' in dependencies:
                self.frameworks.add('React')
            if 'vue' in dependencies:
                self.frameworks.add('Vue.js')
            if 'angular' in dependencies or '@angular/core' in dependencies:
                self.frameworks.add('Angular')
            if 'next' in dependencies:
                self.frameworks.add('Next.js')
            if 'nuxt' in dependencies:
                self.frameworks.add('Nuxt.js')
            if 'svelte' in dependencies:
                self.frameworks.add('Svelte')
            if 'express' in dependencies:
                self.frameworks.add('Express.js')
            if 'fastify' in dependencies:
                self.frameworks.add('Fastify')
            if 'nestjs' in dependencies or '@nestjs/core' in dependencies:
                self.frameworks.add('NestJS')

            # Build tools
            if 'webpack' in dependencies:
                self.build_tools.add('Webpack')
            if 'vite' in dependencies:
                self.build_tools.add('Vite')
            if 'parcel' in dependencies:
                self.build_tools.add('Parcel')
            if 'rollup' in dependencies:
                self.build_tools.add('Rollup')

            # Test frameworks
            if 'jest' in dependencies:
                self.test_frameworks.add('Jest')
            if 'mocha' in dependencies:
                self.test_frameworks.add('Mocha')
            if 'cypress' in dependencies:
                self.test_frameworks.add('Cypress')
            if 'playwright' in dependencies:
                self.test_frameworks.add('Playwright')
            if 'vitest' in dependencies:
                self.test_frameworks.add('Vitest')

        except (json.JSONDecodeError, FileNotFoundError):
            pass

    def _analyze_requirements_txt(self, path: Path):
        """Analyze requirements.txt for Python projects."""
        try:
            with open(path, 'r') as f:
                lines = f.readlines()

            for line in lines:
                package = line.split('==')[0].split('>=')[0].split('<=')[0].strip()

                # Frameworks
                if package in ['django', 'Django']:
                    self.frameworks.add('Django')
                elif package in ['flask', 'Flask']:
                    self.frameworks.add('Flask')
                elif package in ['fastapi', 'FastAPI']:
                    self.frameworks.add('FastAPI')
                elif package == 'tornado':
                    self.frameworks.add('Tornado')

                # Test frameworks
                elif package in ['pytest', 'unittest2']:
                    self.test_frameworks.add('pytest')
                elif package == 'nose':
                    self.test_frameworks.add('nose')

        except FileNotFoundError:
            pass

    def _analyze_pyproject_toml(self, path: Path):
        """Analyze pyproject.toml for Python projects."""
        self.build_tools.add('Poetry/PyProject')

    def _analyze_pom_xml(self, path: Path):
        """Analyze pom.xml for Java Maven projects."""
        self.build_tools.add('Maven')
        self.frameworks.add('Java/Maven')

    def _analyze_gradle(self, path: Path):
        """Analyze build.gradle for Java Gradle projects."""
        self.build_tools.add('Gradle')
        self.frameworks.add('Java/Gradle')

    def _analyze_cargo_toml(self, path: Path):
        """Analyze Cargo.toml for Rust projects."""
        self.build_tools.add('Cargo')
        self.frameworks.add('Rust')

    def _analyze_go_mod(self, path: Path):
        """Analyze go.mod for Go projects."""
        self.build_tools.add('Go Modules')
        self.frameworks.add('Go')

    def _analyze_composer_json(self, path: Path):
        """Analyze composer.json for PHP projects."""
        self.build_tools.add('Composer')

    def _analyze_gemfile(self, path: Path):
        """Analyze Gemfile for Ruby projects."""
        self.build_tools.add('Bundler')
        try:
            with open(path, 'r') as f:
                content = f.read()
            if 'rails' in content.lower():
                self.frameworks.add('Ruby on Rails')
        except FileNotFoundError:
            pass

    def _analyze_pubspec(self, path: Path):
        """Analyze pubspec.yaml for Dart/Flutter projects."""
        self.frameworks.add('Flutter/Dart')
        self.build_tools.add('Pub')

    def _detect_framework_files(self):
        """Detect frameworks by specific file patterns."""
        framework_files = {
            'angular.json': 'Angular',
            'vue.config.js': 'Vue.js',
            'nuxt.config.js': 'Nuxt.js',
            'svelte.config.js': 'Svelte',
            'tailwind.config.js': 'TailwindCSS',
            'webpack.config.js': 'Webpack',
            'vite.config.js': 'Vite',
            'jest.config.js': 'Jest',
            'cypress.json': 'Cypress',
            'playwright.config.js': 'Playwright',
            'docker-compose.yml': 'Docker Compose',
            'Dockerfile': 'Docker',
            '.github/workflows': 'GitHub Actions',
            'manage.py': 'Django',
            'app.py': 'Flask (potential)',
            'main.py': 'Python Application'
        }

        for file_pattern, framework in framework_files.items():
            if (self.project_path / file_pattern).exists():
                if 'config' in file_pattern.lower() or file_pattern in ['angular.json', 'vue.config.js']:
                    self.build_tools.add(framework)
                elif 'test' in framework.lower() or framework in ['Jest', 'Cypress', 'Playwright']:
                    self.test_frameworks.add(framework)
                else:
                    self.frameworks.add(framework)

    def discover_modules(self) -> List[Dict]:
        """Discover modules, components, and key files."""
        modules = []

        # Common source directories
        source_dirs = ['src', 'lib', 'components', 'pages', 'views', 'controllers', 'services', 'models', 'utils', 'app']

        for source_dir in source_dirs:
            source_path = self.project_path / source_dir
            if source_path.exists() and source_path.is_dir():
                modules.extend(self._analyze_directory(source_path, source_dir))

        # Look for main files in root
        main_files = ['main.py', 'app.py', 'index.js', 'index.ts', 'main.js', 'main.ts', 'App.tsx', 'App.jsx']
        for main_file in main_files:
            main_path = self.project_path / main_file
            if main_path.exists():
                modules.append({
                    'name': main_file,
                    'path': main_file,
                    'type': 'Entry Point',
                    'description': f'Main application entry point'
                })

        self.modules = modules
        return modules

    def _analyze_directory(self, dir_path: Path, dir_name: str) -> List[Dict]:
        """Analyze a directory for modules and components."""
        modules = []

        try:
            for item in dir_path.iterdir():
                if item.is_file() and item.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs']:
                    module_info = {
                        'name': item.stem,
                        'path': str(item.relative_to(self.project_path)),
                        'type': self._determine_module_type(item, dir_name),
                        'description': self._extract_description(item)
                    }
                    modules.append(module_info)
                elif item.is_dir() and not item.name.startswith('.'):
                    modules.extend(self._analyze_directory(item, item.name))
        except PermissionError:
            pass

        return modules

    def _determine_module_type(self, file_path: Path, dir_name: str) -> str:
        """Determine the type of module based on file and directory context."""
        file_name = file_path.stem.lower()

        if 'test' in file_name or 'spec' in file_name:
            return 'Test'
        elif dir_name.lower() in ['components', 'component']:
            return 'Component'
        elif dir_name.lower() in ['services', 'service']:
            return 'Service'
        elif dir_name.lower() in ['models', 'model']:
            return 'Model'
        elif dir_name.lower() in ['controllers', 'controller']:
            return 'Controller'
        elif dir_name.lower() in ['views', 'view']:
            return 'View'
        elif dir_name.lower() in ['utils', 'utilities', 'helpers']:
            return 'Utility'
        elif file_name in ['app', 'main', 'index']:
            return 'Entry Point'
        elif 'config' in file_name:
            return 'Configuration'
        else:
            return 'Module'

    def _extract_description(self, file_path: Path) -> str:
        """Extract description from file comments."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:10]  # Check first 10 lines

            for line in lines:
                line = line.strip()
                # Look for ABOUTME comments
                if 'ABOUTME:' in line:
                    return line.split('ABOUTME:')[1].strip().strip('"\'')
                # Look for other comment patterns
                elif line.startswith(('# ', '// ', '/* ', '* ')):
                    comment = re.sub(r'^[#/\*\s]+', '', line).strip()
                    if len(comment) > 10 and not comment.startswith(('TODO', 'FIXME', 'NOTE')):
                        return comment[:100]

            return f"{file_path.suffix[1:].upper()} module"

        except (UnicodeDecodeError, FileNotFoundError):
            return "Module"

    def detect_apis(self) -> List[Dict]:
        """Detect API endpoints and routes."""
        apis = []

        # Patterns for different frameworks
        patterns = {
            'Flask': [r'@app\.route\(["\']([^"\']+)["\']', r'@bp\.route\(["\']([^"\']+)["\']'],
            'Django': [r'path\(["\']([^"\']+)["\']', r'url\(["\']([^"\']+)["\']'],
            'Express': [r'app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']', r'router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'],
            'FastAPI': [r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']', r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']']
        }

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', 'venv', 'env'}]

            for file in files:
                if file.endswith(('.py', '.js', '.ts')):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        for framework, pattern_list in patterns.items():
                            for pattern in pattern_list:
                                matches = re.findall(pattern, content)
                                for match in matches:
                                    if isinstance(match, tuple):
                                        method, endpoint = match[0], match[1]
                                    else:
                                        method, endpoint = 'GET', match

                                    apis.append({
                                        'endpoint': endpoint,
                                        'method': method.upper(),
                                        'file': str(file_path.relative_to(self.project_path)),
                                        'framework': framework
                                    })
                    except (UnicodeDecodeError, FileNotFoundError):
                        continue

        self.apis = apis
        return apis

    def get_git_insights(self) -> Dict:
        """Get Git repository insights."""
        git_info = {}

        if (self.project_path / '.git').exists():
            try:
                # Get recent commits
                result = subprocess.run(['git', 'log', '--oneline', '-10'],
                                      cwd=self.project_path, capture_output=True, text=True)
                if result.returncode == 0:
                    git_info['recent_commits'] = result.stdout.strip().split('\n')[:5]

                # Get branch info
                result = subprocess.run(['git', 'branch', '--show-current'],
                                      cwd=self.project_path, capture_output=True, text=True)
                if result.returncode == 0:
                    git_info['current_branch'] = result.stdout.strip()

                # Get contributor count
                result = subprocess.run(['git', 'shortlog', '-sn'],
                                      cwd=self.project_path, capture_output=True, text=True)
                if result.returncode == 0:
                    contributors = result.stdout.strip().split('\n')
                    git_info['contributors'] = len(contributors)

            except FileNotFoundError:
                git_info['status'] = 'Git not available'
        else:
            git_info['status'] = 'Not a Git repository'

        return git_info

    async def _query_with_sdk(self, prompt: str) -> str:
        """Query Claude using Claude Agent SDK query() function with OAuth token support."""
        response_text = ""
        
        # Check for OAuth token in environment
        oauth_token = os.getenv("CLAUDE_CODE_OAUTH_TOKEN") or os.getenv("HANDBOOK_CLAUDE_OAUTH_TOKEN")
        
        if oauth_token:
            # Ensure CLAUDE_CODE_OAUTH_TOKEN is set for SDK to read automatically
            if not os.getenv("CLAUDE_CODE_OAUTH_TOKEN"):
                os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = oauth_token
        
        try:
            # Use query() function from SDK (handles OAuth tokens automatically)
            async for message in sdk_query(prompt=prompt):
                # Handle assistant messages (streaming text)
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            response_text += block.text
                
                # Handle result messages (final result)
                elif isinstance(message, ResultMessage):
                    if message.result:
                        response_text = message.result
            
            return response_text.strip()
        
        except Exception as e:
            if not oauth_token:
                return f"AI analysis failed: No OAuth token found. Set CLAUDE_CODE_OAUTH_TOKEN or HANDBOOK_CLAUDE_OAUTH_TOKEN environment variable."
            return f"AI analysis failed: {str(e)}"

    async def analyze_with_ai(self, content: str, analysis_type: str) -> str:
        """Analyze content using Claude Agent SDK with OAuth token authentication."""
        
        if not self.enable_ai_analysis:
            return f"AI analysis disabled for {analysis_type}"
        
        prompts = {
                "architecture": f"""Analyze this project structure and provide architectural insights:

{content}

Please identify:
1. Overall architecture pattern (MVC, microservices, etc.)
2. Key design decisions and their rationale
3. Potential improvements or concerns
4. Technology choices analysis

Provide a concise technical analysis suitable for a developer handbook.""",

                "codebase_summary": f"""Analyze this codebase structure and provide a technical summary:

{content}

Focus on:
1. Code organization and modularity
2. Key components and their relationships
3. Technical debt indicators
4. Notable patterns or anti-patterns

Keep it technical and actionable.""",

                "dependencies": f"""Analyze these project dependencies and provide insights:

{content}

Evaluate:
1. Dependency health and security
2. Potential version conflicts
3. Missing critical dependencies
4. Suggestions for optimization

Be specific and actionable."""
        }

        prompt = prompts.get(analysis_type, f"Analyze this {analysis_type}:\n{content}")
        
        return await self._query_with_sdk(prompt)

    async def generate_ai_insights(self):
        """Generate AI-powered insights for the project."""

        # Prepare content for analysis
        project_structure = self._get_project_structure_summary()
        dependencies_summary = self._get_dependencies_summary()

        # Run AI analysis
        try:
            architecture_analysis = await self.analyze_with_ai(project_structure, "architecture")
            codebase_analysis = await self.analyze_with_ai(project_structure, "codebase_summary")
            dependencies_analysis = await self.analyze_with_ai(dependencies_summary, "dependencies")

            self.ai_insights = {
                'architecture': architecture_analysis,
                'codebase': codebase_analysis,
                'dependencies': dependencies_analysis
            }
        except Exception as e:
            print(f"⚠️  AI analysis failed: {str(e)}")
            self.ai_insights = {}

    def _get_project_structure_summary(self) -> str:
        """Get a summary of project structure for AI analysis."""
        summary = f"Project: {self.project_path.name}\n\n"

        summary += f"Languages: {', '.join(self.languages)}\n"
        summary += f"Frameworks: {', '.join(self.frameworks)}\n"
        summary += f"Build Tools: {', '.join(self.build_tools)}\n"
        summary += f"Test Frameworks: {', '.join(self.test_frameworks)}\n\n"

        summary += "Configuration Files:\n"
        for config in self.config_files:
            summary += f"- {config}\n"

        summary += "\nModules:\n"
        for module in self.modules[:20]:  # Limit for AI processing
            summary += f"- {module['name']} ({module['type']}): {module['description']}\n"

        if self.apis:
            summary += "\nAPI Endpoints:\n"
            for api in self.apis[:10]:  # Limit for AI processing
                summary += f"- {api['method']} {api['endpoint']} ({api['framework']})\n"

        return summary

    def _get_dependencies_summary(self) -> str:
        """Get dependencies summary for AI analysis."""
        summary = "Project Dependencies:\n\n"

        # Read package.json if exists
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    if 'dependencies' in data:
                        summary += "Production Dependencies:\n"
                        for dep, version in data['dependencies'].items():
                            summary += f"- {dep}: {version}\n"
                    if 'devDependencies' in data:
                        summary += "\nDevelopment Dependencies:\n"
                        for dep, version in data['devDependencies'].items():
                            summary += f"- {dep}: {version}\n"
            except Exception:
                pass

        # Read requirements.txt if exists
        requirements = self.project_path / "requirements.txt"
        if requirements.exists():
            try:
                with open(requirements) as f:
                    summary += "Python Dependencies:\n"
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            summary += f"- {line.strip()}\n"
            except Exception:
                pass

        return summary if summary != "Project Dependencies:\n\n" else "No dependency files found"

    def generate_handbook(self) -> str:
        """Generate the complete handbook."""
        # Analyze the project
        self.detect_languages()
        self.detect_frameworks_and_tools()
        self.discover_modules()
        self.detect_apis()
        git_info = self.get_git_insights()

        # Get project name
        project_name = self.project_path.name.title()
        current_date = datetime.now().strftime("%Y-%m-%d")

        handbook_content = f"""# HANDBOOK
*AI-Optimized Navigation Handbook for {project_name} Project*
*Last Updated: {current_date}*

## Layer 1: System Overview

### Purpose
{project_name} is a software project built with modern technologies and best practices. This handbook provides comprehensive documentation for AI agents and developers to understand and navigate the codebase effectively.

### Tech Stack
**Programming Languages**: {', '.join(sorted(self.languages)) if self.languages else 'Not detected'}
**Frameworks**: {', '.join(sorted(self.frameworks)) if self.frameworks else 'Not detected'}
**Build Tools**: {', '.join(sorted(self.build_tools)) if self.build_tools else 'Not detected'}
**Testing**: {', '.join(sorted(self.test_frameworks)) if self.test_frameworks else 'Not detected'}

### Architecture Pattern
{self.ai_insights.get('architecture', 'Based on the detected technologies and file structure, this project follows modern software development patterns with clear separation of concerns.')}

### Key Technical Decisions
1. **Language Choice**: {list(self.languages)[0] if self.languages else 'Multiple languages'} selected as primary development language
2. **Framework Selection**: {list(self.frameworks)[0] if self.frameworks else 'Framework-agnostic approach'} chosen for core functionality
3. **Build System**: {list(self.build_tools)[0] if self.build_tools else 'Custom build process'} for dependency management and building
4. **Testing Strategy**: {list(self.test_frameworks)[0] if self.test_frameworks else 'Testing framework to be determined'} for quality assurance

## Layer 2: Module Map

### Core Modules
"""

        # Add modules section
        if self.modules:
            module_types = {}
            for module in self.modules:
                module_type = module['type']
                if module_type not in module_types:
                    module_types[module_type] = []
                module_types[module_type].append(module)

            for module_type, modules in module_types.items():
                handbook_content += f"\n#### {module_type} Modules\n"
                for module in modules[:5]:  # Limit to 5 per type
                    handbook_content += f"**{module['name']}** (`{module['path']}`)\n"
                    handbook_content += f"- {module['description']}\n\n"
        else:
            handbook_content += "\n*Modules will be documented as the project structure is established.*\n"

        # Configuration files section
        if self.config_files:
            handbook_content += f"""
### Configuration Files
{chr(10).join([f'- `{config}`: Configuration file for project setup' for config in self.config_files])}

### AI-Powered Codebase Analysis
{self.ai_insights.get('codebase', '*Codebase analysis in progress...*')}
"""

        handbook_content += f"""
## Layer 3: Integration Guide

### APIs & Interfaces
"""

        # Add API endpoints if detected
        if self.apis:
            api_by_framework = {}
            for api in self.apis:
                framework = api['framework']
                if framework not in api_by_framework:
                    api_by_framework[framework] = []
                api_by_framework[framework].append(api)

            for framework, endpoints in api_by_framework.items():
                handbook_content += f"\n#### {framework} Endpoints\n"
                for endpoint in endpoints[:10]:  # Limit to 10 per framework
                    handbook_content += f"- **{endpoint['method']} {endpoint['endpoint']}** - `{endpoint['file']}`\n"
        else:
            handbook_content += "\n*API endpoints will be documented as they are implemented.*\n"

        # Git information
        if git_info:
            handbook_content += f"""

### Version Control Information
"""
            if 'current_branch' in git_info:
                handbook_content += f"- **Current Branch**: {git_info['current_branch']}\n"
            if 'contributors' in git_info:
                handbook_content += f"- **Contributors**: {git_info['contributors']}\n"
            if 'recent_commits' in git_info:
                handbook_content += f"- **Recent Activity**: Active development with recent commits\n"

        handbook_content += f"""

### Configuration Files
{chr(10).join([f'- `{config}`: Project configuration' for config in self.config_files]) if self.config_files else '- Configuration files to be documented'}

### Dependency Analysis
{self.ai_insights.get('dependencies', '*Dependency analysis in progress...*')}

### Development Workflow
1. **Development**: Follow standard development practices for {list(self.languages)[0] if self.languages else 'the chosen language'}
2. **Building**: Use {list(self.build_tools)[0] if self.build_tools else 'appropriate build tools'} for project compilation
3. **Testing**: Run {list(self.test_frameworks)[0] if self.test_frameworks else 'test suite'} for quality assurance
4. **Deployment**: Follow deployment guidelines for the target environment

## Layer 4: Extension Points

### Design Patterns
Based on the project structure and technologies used:

1. **Modular Architecture**: Code is organized in logical modules for maintainability
2. **Configuration-Driven**: External configuration files manage project settings
3. **Testing Integration**: Built-in support for automated testing
4. **Version Control**: Git-based workflow for collaborative development

### Customization Areas
1. **Adding New Features**: Follow established patterns in the existing modules
2. **Configuration Changes**: Modify configuration files as needed
3. **Testing Extensions**: Add tests following the established testing framework
4. **Build Modifications**: Update build configurations for new requirements

### Key Files for Quick Navigation
"""

        # Add key files
        key_files = []

        # Add main entry points
        main_files = ['main.py', 'app.py', 'index.js', 'index.ts', 'main.js', 'main.ts', 'App.tsx', 'App.jsx']
        for main_file in main_files:
            if (self.project_path / main_file).exists():
                key_files.append(f"- Entry point: `{main_file}`")

        # Add config files
        for config in self.config_files:
            key_files.append(f"- Configuration: `{config}`")

        # Add README if exists
        readme_files = ['README.md', 'README.rst', 'README.txt']
        for readme in readme_files:
            if (self.project_path / readme).exists():
                key_files.append(f"- Documentation: `{readme}`")

        if key_files:
            handbook_content += "\n".join(key_files)
        else:
            handbook_content += "- Key files will be identified as project develops"

        handbook_content += f"""

### Recent Changes & Evolution
{chr(10).join([f'- {commit}' for commit in git_info.get('recent_commits', ['Project initialization'])[:3]]) if git_info.get('recent_commits') else '- Project recently initialized'}

---
*This handbook is optimized for AI agents and developers working on {project_name}. Update this document when significant architectural changes occur.*

**Generated by**: Handbook Generator
**License**: MIT
"""

        return handbook_content

    def save_handbook(self, content: str, filename: str = "HANDBOOK.md") -> str:
        """Save the handbook to a file."""
        output_path = self.project_path / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(output_path)

    async def generate_handbook_with_ai(self) -> str:
        """Generate handbook with AI analysis."""
        print("🤖 Generating AI-powered insights...")
        await self.generate_ai_insights()
        return self.generate_handbook()

    async def save_handbook_with_ai(self, filename: str = "HANDBOOK.md") -> str:
        """Generate and save handbook with AI analysis."""
        content = await self.generate_handbook_with_ai()
        return self.save_handbook(content, filename)


def main():
    """Main function to run the handbook generator."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate Project Handbook with AI Analysis (supports OAuth token authentication)")
    parser.add_argument("--path", "-p", default=".", help="Project path to analyze (default: current directory)")
    parser.add_argument("--output", "-o", default="HANDBOOK.md", help="Output filename (default: HANDBOOK.md)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI analysis (faster but less insightful)")
    parser.add_argument("--oauth-token", help="OAuth token for Claude authentication (alternative to environment variable)")

    args = parser.parse_args()

    # Set OAuth token if provided via command line
    if args.oauth_token:
        os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = args.oauth_token
        if args.verbose:
            print("🔐 OAuth token set from command line argument")

    if args.verbose:
        print(f"Analyzing project at: {args.path}")
        if CLAUDE_SDK_AVAILABLE and not args.no_ai:
            print("🤖 AI analysis enabled (using Claude Agent SDK)")
            if os.getenv("CLAUDE_CODE_OAUTH_TOKEN"):
                print("🔐 OAuth token detected - using Max Plan authentication")
            else:
                print("⚠️  No OAuth token found - set CLAUDE_CODE_OAUTH_TOKEN or HANDBOOK_CLAUDE_OAUTH_TOKEN environment variable")
        else:
            print("⚡ AI analysis disabled")

    async def run_generator():
        try:
            generator = HandbookGenerator(args.path, enable_ai_analysis=not args.no_ai)

            if generator.enable_ai_analysis:
                output_path = await generator.save_handbook_with_ai(args.output)
            else:
                content = generator.generate_handbook()
                output_path = generator.save_handbook(content, args.output)

            print(f"✅ Handbook generated successfully!")
            print(f"📄 Saved to: {output_path}")

            if args.verbose:
                print(f"\n📊 Project Analysis Summary:")
                print(f"   Languages: {', '.join(generator.languages) if generator.languages else 'None detected'}")
                print(f"   Frameworks: {', '.join(generator.frameworks) if generator.frameworks else 'None detected'}")
                print(f"   Modules: {len(generator.modules)} modules found")
                print(f"   APIs: {len(generator.apis)} endpoints detected")
                if generator.ai_insights:
                    print(f"   AI Analysis: ✅ Completed")
                else:
                    print(f"   AI Analysis: ❌ Not available")

        except Exception as e:
            print(f"❌ Error generating handbook: {str(e)}")
            sys.exit(1)

    # Run the async function
    asyncio.run(run_generator())


if __name__ == "__main__":
    main()
