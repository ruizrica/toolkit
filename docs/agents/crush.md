<p align="center">
  <img src="../../assets/crush.png" alt="Crush" width="120">
</p>

# Crush Agent

An expert media optimization specialist with deep knowledge of the Crush CLI toolset and media compression techniques. Helps users achieve optimal file size reduction while maintaining acceptable quality standards.

## When to Use

- Optimizing media files for web, mobile, or storage
- Verifying compression quality after processing
- Validating output integrity of compressed files
- Ensuring media files meet specific size and quality requirements
- Batch processing large media collections
- Troubleshooting compression issues

## Capabilities

- **Compression Strategy** - Analyze files and determine optimal settings
- **Quality Assurance** - Verify output integrity and quality
- **Format Validation** - Confirm outputs match expected specs
- **Batch Processing** - Handle large media collections
- **Troubleshooting** - Diagnose and fix compression issues

## Invocation

```bash
/toolkit:crush-agent Check if my product images were processed correctly
```

## Examples

**Verify Compression:**
```
Prompt: "I just ran crush on my product images folder. Can you check if everything processed correctly?"
```

**Optimize for Web:**
```
Prompt: "Compress these marketing videos for our website but maintain good quality"
```

**Quality Assessment:**
```
Prompt: "Evaluate whether this image compression has degraded quality beyond acceptable levels"
```

## Core Responsibilities

### Compression Strategy & Execution
- Analyze media files to determine optimal compression settings
- Recommend appropriate Crush CLI commands and parameters
- Consider target use cases (web, mobile, print, storage)
- Balance file size reduction with quality preservation

### Quality Assurance & Validation

| Check | Description |
|-------|-------------|
| Output Integrity | Files are not corrupted and can be opened/played |
| Quality Assessment | Compression hasn't degraded quality beyond thresholds |
| Processing Completeness | All intended files were successfully processed |
| Format Validation | Outputs match expected formats and specifications |
| Size Requirements | Compressed files meet target size constraints |

### Technical Expertise
- Understanding various media formats (images, videos, audio)
- Knowing when to use lossy vs lossless compression
- Recognizing quality degradation patterns
- Suggesting mitigation strategies

## Supported Formats

### Images
- JPEG, PNG, WebP, AVIF
- GIF, SVG
- HEIC, HEIF

### Videos
- MP4, WebM, MOV
- AVI, MKV
- GIF (animated)

### Audio
- MP3, AAC, OGG
- WAV, FLAC
- M4A

## Compression Recommendations

| Use Case | Approach |
|----------|----------|
| Web images | WebP with 80-85% quality |
| Web videos | H.264/H.265 with adaptive bitrate |
| Print images | Lossless PNG or high-quality JPEG |
| Storage archival | Maximum compression, quality secondary |
| Mobile apps | AVIF/WebP with aggressive optimization |

## Requirements

- **Crush CLI** - Auto-installed: `brew install charmbracelet/tap/crush`
- **macOS/Linux** - For Homebrew installation

## Workflow Optimization

- Suggest batch processing strategies for large collections
- Recommend preprocessing steps when beneficial
- Provide guidance on organizing compressed media
- Offer performance tips for faster processing

## When NOT to Use

- Non-media file operations
- Text or document processing
- Code analysis or generation
- Tasks not related to media optimization

## See Also

- [Crush CLI Documentation](https://charm.sh/crush)
- [groq-agent](groq.md) - Fast general tasks
