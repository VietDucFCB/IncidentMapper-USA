FROM openjdk:8-jdk-slim

# Set environment variables
ENV HADOOP_VERSION=3.3.6
ENV HADOOP_URL=https://dlcdn.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Install required packages
RUN apt-get update && \
    apt-get install -y wget curl net-tools procps netcat-openbsd ssh rsync python3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download and setup Hadoop
RUN wget -q $HADOOP_URL && \
    tar -xzf hadoop-$HADOOP_VERSION.tar.gz && \
    mv hadoop-$HADOOP_VERSION $HADOOP_HOME && \
    rm hadoop-$HADOOP_VERSION.tar.gz

# Configure SSH
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys

# Set working directory
WORKDIR $HADOOP_HOME

# Copy configuration files
COPY config/core-site.xml $HADOOP_HOME/etc/hadoop/
COPY config/hdfs-site.xml $HADOOP_HOME/etc/hadoop/

# Set entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]