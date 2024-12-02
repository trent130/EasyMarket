# Development Environment Setup

This guide will help you set up your development environment to work on this project.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Node.js (v14 or later)
- npm (usually comes with Node.js)
- Git
- A code editor (we recommend Visual Studio Code)

## Step 1: Clone the Repository

1. Open your terminal
2. Run the following command:
   ```
   git clone https://github.com/trent130/upgraded-octo-couscous.git
   cd upgraded-octo-couscous
   ```

## Step 2: Install Dependencies

1. In the project root directory, run:
   ```
   npm install
   ```

## Step 3: Set Up Environment Variables

1. Copy the `.env.example` file to `.env.local`:
   ```
   cp .env.example .env.local
   ```
2. Open `.env.local` in your text editor and fill in the necessary values

## Step 4: Set Up the Database

1. Install PostgreSQL if you haven't already
2. Create a new database for the project
3. Update the database connection string in your `.env.local` file

## Step 5: Run Migrations

1. Run the following command to set up your database schema:
   ```
   npm run migrate
   ```

## Step 6: Start the Development Server

1. Run the following command:
   ```
   npm run dev
   ```
2. Open your browser and navigate to `http://localhost:3000`

## Running Tests

To run the test suite, use the following command:
```
npm test
```

## Linting

To lint your code, run:
```
npm run lint
```

## Building for Production

To create a production build, use:
```
npm run build
```

## Troubleshooting

If you encounter any issues during setup, please check the following:

1. Ensure all prerequisites are correctly installed
2. Make sure all environment variables are properly set
3. Check that your database is running and accessible
4. Ensure you have the necessary permissions to install packages and run scripts

If you still face issues, please refer to the [Troubleshooting Guide](./troubleshooting.md) or open an issue on the GitHub repository.

## Contributing

Please read our [Contributing Guidelines](./CONTRIBUTING.md) before making any changes to the project.

