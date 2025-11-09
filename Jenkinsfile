pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'sonarqube'  
    }

    stages {

        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/Dhananjaydk15/ScanShield_backend.git'
            }
        }

stage('SonarQube Analysis') {
    steps {
        sh """
        docker run --rm --network app-network \
            -e SONAR_HOST_URL=http://sonarqube:9000 \
            -e SONAR_LOGIN=squ_765a483389ed35d74c1c524f14dc234f3bcf65cb \
            -v $WORKSPACE:/usr/src \
            sonarsource/sonar-scanner-cli \
            -Dsonar.projectKey=ScanShield \
            -Dsonar.sources=/usr/src
        """
    }
}

        stage('Quality Gate') {
            steps {
                waitForQualityGate abortPipeline: true
            }
        }

        stage('Build App with Docker Compose') {
            steps {
                sh "docker compose build"
            }
        }

        stage('Deploy App') {
            steps {
                sh """
                docker compose down
                docker compose up -d --force-recreate
                """
            }
        }
    }
}
