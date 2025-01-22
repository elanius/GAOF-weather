# Use the official Node.js 18 image as the base image
FROM node:23

# Set the working directory
WORKDIR /app

# Set npm proxy configuration
RUN npm config set proxy http://sub.proxy.att.com:8080 && \
    npm config set https-proxy http://sub.proxy.att.com:8080 && \
    npm config set strict-ssl false

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the React application
RUN npm run build

# Expose the port the app runs on
EXPOSE 8000

# Start the application
CMD ["npm", "start"]

