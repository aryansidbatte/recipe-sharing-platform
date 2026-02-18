# Recipe Sharing Platform

**Full-stack collaborative recipe management web application**

Built as a team project for UCSC CSE 183 (Spring 2025). This platform enables users to create, share, and manage recipes with ingredient tracking and collaborative editing features.

## Links

- **Forked from**: [ucsc2025-cse183/project-12](https://github.com/ucsc2025-cse183/project-12)

## Tech Stack

- **Backend**: Python 4 Web (py4web), SQLite
- **Frontend**: JavaScript (30.1%), HTML (25.7%), CSS (12.0%)
- **UI Framework**: Bulma CSS
- **Team Size**: 7 contributors, 85+ commits

## Key Features

- User authentication and authorization
- Create, read, update, delete (CRUD) operations for recipes
- Ingredient management with relational database schema
- Collaborative recipe editing with role-based permissions
- Responsive design for mobile and desktop

## Architecture Highlights

- **Database Design**: Many-to-many relationships between recipes and ingredients using junction tables
- **RESTful API**: Clean routing with py4web controllers
- **Team Collaboration**: Managed code reviews and coordinated development across 5-person team
- **Testing**: Backend test suite and CI pipeline integration

## My Contributions

- Implemented recipe card ingredient display system with database integration
- Built user authorization and role-based editing permissions for collaborative recipe management
- Added image upload support for recipe photos
- Refactored index controllers and started recipe CRUD implementation
- Coordinated merge requests and code reviews across team (merged PR #11)

## Screenshots

### Recipe List View
![Recipe List View](/01-main-page.png)
*Full recipe display showing ingredients fetched from SQLite database with real-time integration*

### Recipe Creation & Edit Interface
![Recipe Edit Form](/02-recipe-creation.png)
*CRUD interface with image upload functionality and ingredient management*

### Recipe Added
![Recipes List](/03-recipe-added.png)
