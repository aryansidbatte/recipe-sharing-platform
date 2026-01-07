# README# Recipe Sharing Platform

**Full-stack collaborative recipe management web application**

Built as a team project for UCSC CSE 183 (Spring 2025). This platform enables users to create, share, and manage recipes with ingredient tracking and collaborative editing features.

## 🔗 Links
- **Live Demo**: [Add if deployed, otherwise remove this line]
- **Forked from**: [ucsc2025-cse183/project-12](https://github.com/ucsc2025-cse183/project-12)

## 🛠️ Tech Stack

- **Backend**: Python 4 Web (py4web), SQLite
- **Frontend**: JavaScript (30.1%), HTML (25.7%), CSS (12.0%)
- **UI Framework**: Bulma CSS
- **Team Size**: 7 contributors, 85+ commits

## ✨ Key Features

- User authentication and authorization
- Create, read, update, delete (CRUD) operations for recipes
- Ingredient management with relational database schema
- Collaborative recipe editing with role-based permissions
- Responsive design for mobile and desktop

## 🏗️ Architecture Highlights

- **Database Design**: Many-to-many relationships between recipes and ingredients using junction tables
- **RESTful API**: Clean routing with py4web controllers
- **Team Collaboration**: Managed code reviews and coordinated development across 5-person team
- **Testing**: Backend test suite and CI pipeline integration

## 💻 My Contributions

[IMPORTANT: Check your git commits and add 3-5 specific features YOU built. Examples:]
- Implemented recipe CRUD endpoints and SQLite schema design
- Built pytest automation suite reducing testing time by 48 hours
- Coordinated code reviews and merge conflict resolution for team of 7
- Designed responsive UI components using Bulma framework
- [Add more based on your actual commits]

## 🚀 Setup & Installation

```bash
# Clone repository
git clone https://github.com/aryansidbatte/recipe-sharing-platform.git
cd recipe-sharing-platform

# Install dependencies
pip install py4web

# Run development server
py4web run apps

# Access at http://localhost:8000
