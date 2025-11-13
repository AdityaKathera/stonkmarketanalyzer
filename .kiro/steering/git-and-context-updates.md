---
inclusion: always
---

# Git and Context Update Requirements

## CRITICAL: Always Update Documentation

After completing ANY feature, bug fix, or significant change:

### 1. Git Commit (REQUIRED)
```bash
git add -A
git commit -m "Descriptive message about what changed"
git push origin main
```

### 2. Update AI_SESSION_CONTEXT.md (REQUIRED)

Add to the appropriate section:
- Feature name and status
- Files created/modified
- New endpoints or functions
- Key features and capabilities
- Deployment status
- Update "Last Updated" timestamp

### 3. Create Feature Documentation (for major features)

For significant features, create:
- `FEATURE_NAME_PLAN.md` - Implementation plan
- `FEATURE_NAME_COMPLETE.md` - Final documentation (if needed)

## Example Workflow

1. Build feature
2. Test locally
3. Deploy to production
4. Commit to git with clear message
5. Update AI_SESSION_CONTEXT.md
6. Push everything

## Why This Matters

- Future AI assistants need context
- User can track what was built
- Git history stays clean and documented
- Easy to rollback if needed

## Template for AI_SESSION_CONTEXT.md Updates

```markdown
### ✅ Feature Name - COMPLETE (Date)
- **Status**: ✅ Deployed and working
- **Component**: File paths
- **Backend**: Services/endpoints
- **Features**:
  - Feature 1
  - Feature 2
- **Documentation**: Links to docs
```

---

**Remember**: No feature is complete until it's committed and documented!
