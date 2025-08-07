# SafeZone - Community Safety Checker

## Overview

SafeZone is a web application that allows users to search for registered offenders by ZIP code. The application provides an educational tool for community safety awareness, featuring a clean, teen-friendly interface with mapping capabilities to visualize offender locations. Built as a Flask web application, it currently uses mock data but is designed to be easily integrated with real offender registry APIs.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **UI Framework**: Bootstrap 5 for responsive design and components
- **Styling**: Custom CSS with CSS variables for consistent theming and modern gradients
- **JavaScript**: Vanilla JavaScript with class-based architecture for client-side functionality
- **Mapping**: Leaflet.js integration for displaying offender locations on interactive maps
- **Icons**: Font Awesome for consistent iconography

### Backend Architecture
- **Framework**: Flask (Python) following a simple MVC pattern
- **Routing**: RESTful API design with separate routes for page rendering and data endpoints
- **Data Layer**: Mock data module (`mock_data.py`) that can be easily replaced with real API integrations
- **Validation**: Server-side ZIP code validation with proper error handling
- **Response Format**: JSON API responses with consistent success/error structure

### Application Structure
- **Entry Point**: `main.py` serves as the application entry point
- **Core Application**: `app.py` contains all Flask routes and business logic
- **Data Source**: `mock_data.py` provides sample data with realistic offender information
- **Templates**: HTML templates in `templates/` directory for page rendering
- **Static Assets**: CSS and JavaScript files organized in `static/` directory

### Security Considerations
- Session secret key configuration via environment variables
- Input sanitization for ZIP code searches
- CSRF protection through Flask's built-in mechanisms

## External Dependencies

### Frontend Libraries
- **Bootstrap 5**: UI component framework and responsive grid system
- **Leaflet.js**: Open-source mapping library for displaying interactive maps
- **Font Awesome**: Icon library for consistent UI elements

### Backend Dependencies
- **Flask**: Python web framework for HTTP handling and templating
- **Python Standard Library**: Logging, OS environment variable handling

### Future Integration Points
- **Offender Registry APIs**: Currently using mock data, designed for easy integration with state or federal offender registry APIs
- **Geocoding Services**: Prepared for integration with mapping services to convert addresses to coordinates
- **Database**: Architecture supports future database integration for caching and user data storage

### Development Tools
- **Logging**: Built-in Python logging for debugging and monitoring
- **Environment Configuration**: Support for environment-based configuration management