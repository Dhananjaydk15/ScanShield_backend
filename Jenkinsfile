pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'sonarqube'
        SONAR_TOKEN = 'squ_e68fe8e90af5b9a142b05bc33e321ec6fea2aa7b'
    }

    stages {

        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/Dhananjaydk15/ScanShield_backend.git'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${env.SONARQUBE_SERVER}") {
                    sh """
                    /opt/sonar-scanner/sonar-scanner-7.3.0.5189-linux-x64/bin/sonar-scanner \
                        -Dsonar.projectKey=ScanShield \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://localhost:9000 \
                        -Dsonar.token=$SONAR_TOKEN
                    """
                }
            }
        }

        /*** 🔥 Add OWASP Dependency Check Here ***/
        stage('OWASP Dependency Check') {
            steps {
                sh """
                docker run --rm \
                  -v \$(pwd):/src \
                  owasp/dependency-check:latest \
                  --scan /src \
                  --format ALL \
                  --out /src/dependency-check-report \
                  --project ScanShield
                """
            }
        }

        stage('Publish OWASP Reports') {
            steps {
                publishHTML(target: [
                    reportDir: 'dependency-check-report',
                    reportFiles: 'dependency-check-report.html',
                    reportName: 'OWASP Dependency Check Report'
                ])
            }
        }
        /*** 🔥 End OWASP Section ***/

        stage('Build App') {
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

    post {
        success {
            emailext(
                to: 'dhananjaykhairnar15@gmail.com',
                subject: "SUCCESS: Build #${env.BUILD_NUMBER}",
                body: """<p>Hi Team,</p>
                         <p>The Jenkins build <b>#${env.BUILD_NUMBER}</b> completed successfully.</p>
                         <p>Regards,<br>Jenkins</p>""",
                mimeType: 'text/html'
            )
        }
    }
}
