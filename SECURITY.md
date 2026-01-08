# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within Python Accounting, please send an email to security@microbooks.io.

**Please do not report security vulnerabilities through public GitHub issues.**

You should receive a response within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity.

## Security Considerations

### Ledger Integrity

Python Accounting includes built-in tamper protection for the ledger:

1. **Transaction Hashing**: Each ledger entry includes a hash that verifies its integrity
2. **Posted Transaction Protection**: Posted transactions cannot be modified or deleted
3. **Audit Trail**: All changes are tracked and logged

### Database Security

- Always use parameterized queries (handled by SQLAlchemy ORM)
- Use database-level encryption for sensitive data
- Implement proper access controls at the database level

### Best Practices

1. **Never expose raw error messages** to end users in production
2. **Use environment variables** for database credentials
3. **Enable HTTPS** when deploying with the CLI or API integrations
4. **Regularly update dependencies** to patch security vulnerabilities
5. **Implement proper authentication** when using the event system for webhooks
