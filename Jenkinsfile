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
        docker run --rm \
            -e SONAR_HOST_URL=http://localhost:9000 \
            -e SONAR_LOGIN="squ_8c1b2e9d1c6f0cc61fee642291520e040fb7c4c0" \
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
