# Project Context: MenuFlow

## Project Name
MenuFlow

## Domain
Dynamic AI Data

## Problem Statement
Restaurants that frequently update their menus struggle to keep POS systems, Uber Eats, DoorDash, websites, and dashboards consistent. Updating each platform manually is slow, repetitive, and error-prone.

MenuFlow solves this by letting a restaurant owner enter a menu update once through an AI chatbot. The system converts that unstructured input into structured menu data and stores it in a database/dashboard.

## What I am building
A restaurant AI assistant that integrates with POS systems to:
- update and add products to menu and other platforms (like Uber Eats, DoorDash, Grubhub, etc.) via chat (and images if needed)
- example: "add a new wing dinner to the uber eats menu called 10 Wing Dinner for $15, and use tenwingdinner.jpg as the photo" 
- manage customer data (emails, phone numbers)
- send promotions and deals
- track orders and customer behavior
- eventually automate interactions with delivery platforms
- Be able to sync with POS systems (Square, Toast, Lightspeed, Clover, Brink etc.) to be able to look at sales data, make edits, etc.

## Why this is Dynamic AI Data
This project demonstrates Dynamic AI Data because it takes changing, unstructured restaurant menu information and transforms it into structured, usable data in real time. 

The app uses:
- AI parsing to understand menu update requests
- structured data extraction for item name, price, category, description, and image
- database storage for updated menu records
- simulated synchronization across multiple platforms
- RAG-style retrieval so the AI can reference existing menu items before making changes

## Target users
- small to medium restaurant owners

## Core idea
Help restaurants update menus on multiple platforms autonomously (uber eats, doordash, etc.), synchronize with pos systems,         increase repeat customers, and automate marketing using their existing data.

## Key features (initial idea)
- chatbot for menu updates(with images), price changes, item additions, item deletions, etc.
- customer database
- promotions system (email/SMS)
- simple dashboard
- order tracking

## Future ideas (NOT MVP)
- analytics + predictions

## Constraints
- must be simple yet impactful (usable)
- understandable to someone with basic technical knowledge
- privacy-safe (no leaking customer data)
- realistic for 6 weeks

## Proposed Tech Stack (MVP)

Frontend:
- Next.js (React) OR simple React app
- Tailwind CSS (optional, for faster UI)

Backend:
- FastAPI (Python)

Database:
- PostgreSQL (via Supabase)

AI / RAG:
- LLM (Gemini or OpenAI)
- Embeddings + vector storage (Supabase or simple local approach for MVP)

Other:
- REST API architecture
- JSON structured outputs from AI

## AWS Cloud Setup

Frontend:
- AWS Amplify Hosting

Backend/API:
- FastAPI hosted on AWS App Runner

AI Agent:
- Runs inside the FastAPI backend as an agent endpoint
- Receives menu updates
- Retrieves existing menu data
- Converts updates into structured JSON
- Sends actions to the database

Database:
- Amazon RDS PostgreSQL

RAG / Vector Search:
- PostgreSQL with pgvector
- Store menu item embeddings
- Retrieve similar/existing menu items before updating

Storage:
- Amazon S3 for menu item images

Secrets:
- AWS Secrets Manager for API keys

MVP Sync:
- Simulated sync statuses for POS, Uber Eats, DoorDash, and website
