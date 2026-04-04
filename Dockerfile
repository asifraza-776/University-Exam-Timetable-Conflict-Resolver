# Use an official Node.js image as the base
FROM node:20-slim

# Install Python 3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy package.json and install Node dependencies
COPY package*.json ./
RUN npm install

# Copy requirements.txt and install Python dependencies
COPY requirements.txt ./
# We set up a virtual environment inside Docker as well to run python packages smoothly without PEP-668 errors on modern Debian
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (Render/Railway sets PORT env var)
EXPOSE 3000

# Start the application
CMD ["node", "server.js"]
