# API Services Documentation

## Overview
This directory contains consolidated API-related code for the application. The structure is organized to improve maintainability and clarity.

## Directory Structure
- **admin.ts**: Contains admin-related API functions.
- **auth.ts**: Contains authentication-related API functions.
- **categories.ts**: Contains category-related API functions.
- **marketplace.ts**: Contains marketplace-related API functions.
- **orders.ts**: Contains order-related API functions.
- **payment.ts**: Contains payment-related API functions.
- **students.ts**: Contains student-related API functions.
- **reviews.ts**: Contains review-related API functions.
- **security.ts**: Contains security-related API functions.
- **staticpages.ts**: Contains static page-related API functions.
- **utils.ts**: Contains shared utility functions for API handling.
- **index.ts**: Central export for all API modules.

## Adding New API Modules
To add a new API module:
1. Create a new TypeScript file in this directory.
2. Implement the necessary functions and interfaces.
3. Export the functions from the new file.
4. Update the `index.ts` file to include the new module.

## Usage
Import the necessary API functions in your components or services as follows:
```typescript
import { adminApi } from './services/api';
```

## Conclusion
This structure aims to provide a clear and maintainable organization for API-related code, making it easier for developers to navigate and extend the API functionalities in the future.
