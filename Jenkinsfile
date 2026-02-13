pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'sonarqube'
        SONAR_TOKEN = 'squ_96754e8f46fcf62b692605612352ed6ca4e8bfb0'
        APP_URL = 'http://localhost:8000'
        IMAGE_NAME = 'scanshield-app:latest'
        ZAP_REPORT_DIR = 'zap-reports'
    }

    stages {

        // ================== DEBUG USER ==================
        // stage('Debug User') {
        //     steps {
        //         script {
        //             wrap([$class: 'BuildUser']) {
        //                 echo "BUILD_USER_ID: ${env.BUILD_USER_ID}"
        //                 echo "BUILD_USER: ${env.BUILD_USER}"
        //             }
        //         }
        //     }
        // }

        // ================== 1. CLONE ==================
        stage('Clone Code') {
            steps {
                git branch: 'main', url: 'https://github.com/Dhananjaydk15/ScanShield_backend.git'
            }
        }

        // ================== 2. CODE LINTING ==================
        // stage('Code Linting') {
        //     steps {
        //         sh """
        //         pip install flake8 || true
        //         flake8 . --output-file=flake8-report.txt || true
        //         """
        //     }
        // }

        // ================== 3. SECRETS SCAN ==================
        // stage('Secrets Scan (Gitleaks)') {
        //     steps {
        //         sh "gitleaks detect --source . --report-format json --report-path gitleaks-report.json || true"
        //     }
        // }

        // ================== 4. SAST ==================
        // stage('SAST - SonarQube Analysis') {
        //     steps {
        //         withSonarQubeEnv("${env.SONARQUBE_SERVER}") {
        //             sh """
        //             sonar-scanner \
        //                 -Dsonar.projectKey=ScanShield \
        //                 -Dsonar.sources=. \
        //                 -Dsonar.host.url=http://localhost:9000 \
        //                 -Dsonar.login=${SONAR_TOKEN}
        //             """
        //         }
        //     }
        // }

        // ================== 5. SBOM ==================
        // stage('Generate SBOM (Syft)') {
        //     steps {
        //         sh "syft . -o json > sbom.json || true"
        //     }
        // }

        // ================== 6. SCA ==================
        // stage('SCA - Trivy FS Scan') {
        //     steps {
        //         sh "trivy fs . -o trivy-fs-report.json --format json || true"
        //     }
        // }

        // ================== 7. SECURITY GATE ==================
        // stage('Security Gate #1') {
        //     steps {
        //         script {
        //             echo "Security Gate logic here"
        //         }
        //     }
        // }

        // ================== 8. BUILD ==================
        stage('Build App') {
            steps {
                sh """
                echo "Building Docker image..."
                docker build -t ${IMAGE_NAME} .
                echo "Build completed successfully."
                """
            }
        }

        // ================== 9. IMAGE SCAN ==================
        // stage('Trivy Image Scan') {
        //     steps {
        //         sh "trivy image ${IMAGE_NAME} --format json -o trivy-image-report.json || true"
        //     }
        // }

        // ================== 10. SECURITY GATE ==================
        // stage('Security Gate #2') {
        //     steps {
        //         script {
        //             echo "Security Gate #2 logic"
        //         }
        //     }
        // }

        //================== 11. DEPLOY ==================
        stage('Deploy Application') {
            steps {
                sh """
                docker rm -f scanshield || true
                docker run -d --name scanshield -p 8000:8000 ${IMAGE_NAME}
                """
            }
        }

        // ================== 12. DAST ==================
        // stage('DAST - OWASP ZAP Scan') {
        //     steps {
        //         sh "echo ZAP Scan"
        //     }
        // }

        // ================== 13. PUBLISH REPORTS ==================
        // stage('Publish Reports') {
        //     steps {
        //         echo "Publish Reports"
        //     }
        // }

    }

    // ================== POST BUILD ==================
    // post {
    //     always {
    //         archiveArtifacts artifacts: '**/*.json, **/*.xml, **/*.txt, **/*.html', fingerprint: true
    //     }
    //
    //     success {
    //         emailext(
    //             to: "dhananjaykhairnar15@gmail.com",
    //             subject: "SUCCESS: Build #${env.BUILD_NUMBER}",
    //             body: "<p>Build Completed Successfully.</p>",
    //             mimeType: 'text/html'
    //         )
    //     }
    //
    //     failure {
    //         emailext(
    //             to: "dhananjaykhairnar15@gmail.com",
    //             subject: "FAILED: Build #${env.BUILD_NUMBER}",
    //             body: "<p>Build Failed.</p>",
    //             mimeType: 'text/html'
    //         )
    //     }
    // }
}
