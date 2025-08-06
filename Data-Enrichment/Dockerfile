FROM node:18 AS frontend-builder

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source code
COPY public ./public
COPY src ./src
COPY index.js ./
COPY index.css ./
COPY app.js ./
COPY auth.js ./
COPY components ./components
COPY services ./services
COPY tailwind.config.js ./
COPY .env.production ./

# Build frontend
RUN npm run build

# Use Python image for backend
FROM python:3.10-slim

WORKDIR /app

# Copy Python requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY main.py .

# Copy frontend build from previous stage
COPY --from=frontend-builder /app/build ./static

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port for API
EXPOSE 5001

# Run the application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]
