# schubAI Issue Tracker

## Active Issues

### Critical Priority

#### Build System
- 🔴 **[BUILD-001]** Backend build failing due to missing files
  - **Status**: New
  - **Impact**: Backend service not building
  - **Details**: Missing files: package.json, yarn.lock, tsconfig.json
  - **Solution**: Create necessary Node.js configuration files
  - **Related PR**: #TBD

#### OCR Service
- 🔴 **[OCR-001]** Model download time impacts initial startup
  - **Status**: In Progress
  - **Assigned**: @maccie01
  - **Impact**: Extended container startup time (180s)
  - **Workaround**: Extended health check start period
  - **Solution**: Implement persistent model caching
  - **Related PR**: #TBD

### High Priority

#### Resource Management
- 🟠 **[RES-001]** Memory allocation needs optimization
  - **Status**: Under Investigation
  - **Impact**: Potential resource constraints during peak usage
  - **Next Steps**: Implement monitoring and analysis
  - **Related Issues**: RES-002, MON-001

#### Monitoring
- 🟠 **[MON-001]** Missing Grafana dashboards for Loki metrics
  - **Status**: Planned
  - **Impact**: Limited visibility into log metrics
  - **Dependencies**: Loki configuration
  - **Related PR**: #TBD

### Medium Priority

#### Security
- 🟡 **[SEC-001]** Container permissions need review
  - **Status**: Planned
  - **Impact**: Potential security vulnerabilities
  - **Dependencies**: Security audit completion
  - **Related Issues**: SEC-002

#### Documentation
- 🟡 **[DOC-001]** API documentation incomplete
  - **Status**: In Progress
  - **Impact**: Developer onboarding difficulty
  - **Assigned**: @maccie01
  - **Related PR**: #TBD

### Low Priority

#### UI/UX
- 🟢 **[UI-001]** Add dark mode support
  - **Status**: Planned
  - **Impact**: User preference limitation
  - **Dependencies**: None
  - **Related PR**: #TBD

## Recently Resolved

### Week of February 5, 2024

#### Infrastructure
- ✅ **[INF-001]** Docker network configuration
  - **Resolved**: 2024-02-04
  - **Solution**: Implemented bridge network with proper isolation
  - **PR**: #TBD

#### OCR Service
- ✅ **[OCR-002]** MKLDNN cache capacity error
  - **Resolved**: 2024-02-04
  - **Solution**: Disabled MKLDNN for ARM64 compatibility
  - **PR**: #TBD

#### GitHub Actions
- ✅ **[CI-001]** Docker Hub authentication failing
  - **Resolved**: 2024-02-05
  - **Solution**: Added proper Docker Hub credentials to GitHub secrets
  - **PR**: #TBD

## Known Limitations

### Current Version (1.0.0-alpha)

1. **OCR Service**
   - Limited batch processing capabilities
   - Initial startup delay due to model downloads
   - Memory usage spikes during processing

2. **Resource Management**
   - Manual scaling only
   - Fixed resource allocation
   - No auto-recovery

3. **Monitoring**
   - Basic metrics collection
   - Limited alert configurations
   - Manual dashboard setup required

## Build Status

### OCR Service
- ✅ Build successful
- Build time: 168.4s
- Multi-stage build with optimizations
- ARM64 compatibility confirmed

### Backend Service
- ❌ Build failed
- Error: Missing configuration files
  - package.json
  - yarn.lock
  - tsconfig.json
- Status: Needs immediate attention

### Frontend Service
- ⏳ Build pending
- Blocked by backend service build
- Dependencies need review

## Next Actions

1. **Critical**
   - Create missing Node.js configuration files
   - Fix backend service build
   - Test service dependencies

2. **High Priority**
   - Complete monitoring setup
   - Implement resource optimizations
   - Add proper error handling

3. **Medium Priority**
   - Review security configurations
   - Complete API documentation
   - Implement logging improvements

## Feature Requests

### Under Review

1. **High Priority**
   - 📋 **[FR-001]** Distributed training support
   - 📋 **[FR-002]** Auto-scaling configuration
   - 📋 **[FR-003]** Advanced caching layer

2. **Medium Priority**
   - 📋 **[FR-004]** Custom model training UI
   - 📋 **[FR-005]** Batch document processing
   - 📋 **[FR-006]** Export/Import functionality

3. **Low Priority**
   - 📋 **[FR-007]** Plugin system
   - 📋 **[FR-008]** Custom theme support
   - 📋 **[FR-009]** API key management UI

## Issue Templates

### Bug Report Template
```markdown
**Description**
[Clear description of the bug]

**Steps to Reproduce**
1. [First Step]
2. [Second Step]
3. [Additional Steps...]

**Expected Behavior**
[What should happen]

**Actual Behavior**
[What actually happens]

**Environment**
- OS: [e.g., macOS 14.1]
- Docker Version: [e.g., 24.0.7]
- Component Version: [e.g., OCR Service 1.0.0]

**Additional Context**
[Any other relevant information]
```

### Feature Request Template
```markdown
**Feature Description**
[Clear description of the proposed feature]

**Use Case**
[Explain when and how this feature would be used]

**Expected Benefits**
[List the benefits of implementing this feature]

**Alternative Solutions**
[Any alternative solutions or features considered]

**Additional Context**
[Any other relevant information]
```

## Contributing to Issue Resolution

1. **Picking Up Issues**
   - Comment on the issue you want to work on
   - Wait for assignment confirmation
   - Create a feature branch
   - Follow development guidelines

2. **Submitting Fixes**
   - Ensure all tests pass
   - Update documentation
   - Create a pull request
   - Link related issues

3. **Review Process**
   - Code review required
   - CI/CD checks must pass
   - Documentation updates verified
   - Integration tests passed

## Issue Prioritization

### Priority Levels
- 🔴 **Critical**: Immediate attention required
- 🟠 **High**: Significant impact on functionality
- 🟡 **Medium**: Important but not urgent
- 🟢 **Low**: Minor improvements or enhancements

### Response Times
- Critical: < 24 hours
- High: < 3 days
- Medium: < 1 week
- Low: < 2 weeks

## Support Channels

- GitHub Issues: Primary channel for bug reports and feature requests
- Discussions: For general questions and community support
- Pull Requests: For code contributions and fixes 