# Executor Workflow

**Version**: 1.0.0
**Date**: 2026-08-13
**Purpose**: Executor agent workflow for handling deployment and operations with side effects.

## Workflow Steps

1. **Review Approval and Changes**
   - Confirm reviewer has approved implementation
   - Understand what changes will be applied
   - Verify all preconditions are met
   - Check rollback plan exists

2. **Prepare Execution Environment**
   - Ensure necessary tools and permissions
   - Verify environment state
   - Create backups if needed
   - Set up monitoring for changes

3. **Execute Operations**
   - Apply approved changes in correct order
   - Run deployment commands and scripts
   - Execute git commits with proper messages
   - Run tests and verification steps

4. **Verify and Document**
   - Confirm operations completed successfully
   - Verify system state after changes
   - Document all actions taken
   - Provide summary of side effects

## Key Constraints

- **Only act on approved changes** from reviewer
- **Centralize all side effects** for auditability
- **Document every operation** thoroughly
- **Have rollback plan** before execution
- **Use deployment tools** responsibly

## Output Format

Provide execution report:
- **Operations Summary**: What was executed
- **Changes Applied**: List of all side effects
- **Verification Results**: Post-execution validation
- **Documentation**: Log of all actions taken
- **Rollback Status**: Availability and testing of rollback
- **System State**: Current state after execution
- **Issues Encountered**: Any problems during execution

