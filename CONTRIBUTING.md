# Contributing to Basta Claude Skill

Thank you for your interest in contributing! This document provides guidelines for contributing to the Basta Claude Skill.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if the issue already exists in [GitHub Issues](../../issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment (Claude version, OS, etc.)

### Suggesting Enhancements

We welcome suggestions for:
- New API features or workflows
- Additional code examples
- Improved documentation
- Better error handling
- Performance improvements

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/basta-claude-skill.git
   cd basta-claude-skill
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Update documentation as needed
   - Add examples if applicable

4. **Test your changes**
   - Test the skill in Claude
   - Verify all scripts run without errors
   - Check that documentation renders correctly

5. **Commit your changes**
   ```bash
   git commit -m "Add feature: brief description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Explain why the change is needed

## Development Guidelines

### Documentation

- Use clear, concise language
- Include code examples where helpful
- Follow existing markdown formatting
- Update the CHANGELOG.md

### Code Examples

- Include comments explaining non-obvious code
- Use meaningful variable names
- Follow Python PEP 8 style guide for Python code
- Test all code examples before committing

### Skill Structure

When modifying the skill:

- **SKILL.md** - Core workflows only, keep concise
- **references/** - Detailed documentation
- **scripts/** - Executable, tested code
- **examples/** - Sample implementations

### Testing Checklist

Before submitting:

- [ ] Skill loads in Claude without errors
- [ ] All code examples are tested and working
- [ ] Documentation is clear and accurate
- [ ] No broken links in markdown
- [ ] CHANGELOG.md is updated
- [ ] Commit messages are clear

## Skill Packaging

If you modify the skill structure:

1. **Repackage the skill**
   ```bash
   # From the skill-creator scripts
   python3 package_skill.py skill/ releases/
   ```

2. **Test the packaged skill**
   - Upload to Claude
   - Verify it works as expected

3. **Update version number** in CHANGELOG.md

## Code of Conduct

- Be respectful and constructive
- Welcome newcomers
- Focus on what's best for the community
- Show empathy toward others

## Questions?

- Open a [GitHub Discussion](../../discussions)
- Check existing [Issues](../../issues)
- Email: [hi@basta.app](mailto:hi@basta.app) for Basta-specific questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in the README and release notes. Thank you for making this skill better! 🙏
