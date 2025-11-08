pipeline {
    agent any

    stages {

        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/Dhananjaydk15/ScanShield_backend.git'
            }
        }

        stage('Build App with Docker Compose') {
            steps {
                script {
                    sh """
                    docker compose build
                    """
                }
            }
        }

        stage('Deploy App') {
            steps {
                script {
                    sh """
                    docker compose down
                    docker compose up -d --force-recreate
                    """
                }
            }
        }
    }
}
