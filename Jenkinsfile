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
stage('Debug User') {
    steps {
        script {
            wrap([$class: 'BuildUser']) {
                echo "BUILD_USER_ID: ${env.BUILD_USER_ID}"
                echo "BUILD_USER: ${env.BUILD_USER}"
            }
        }
    }
}
        /* ================== 1. CLONE ================== */
        stage('Clone Code') {
            steps {
                git branch: 'main', url: 'https://github.com/Dhananjaydk15/ScanShield_backend.git'
            }
        }

        /* ================== 2. CODE LINTING ================== */
        stage('Code Linting') {
            steps {
                sh """
                pip install flake8 || true
                flake8 . --output-file=flake8-report.txt || true
                """
            }
        }

        /* ================== 3. SECRETS SCAN ================== */
        stage('Secrets Scan (Gitleaks)') {
            steps {
                sh """
                gitleaks detect --source . --report-format json --report-path gitleaks-report.json || true
                """
            }
        }

        /* ================== 4. SAST (SonarQube) ================== */
        stage('SAST - SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${env.SONARQUBE_SERVER}") {
                    sh """
                    /opt/sonar-scanner/sonar-scanner-7.3.0.5189-linux-x64/bin/sonar-scanner \
                        -Dsonar.projectKey=ScanShield \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://localhost:9000 \
                        -Dsonar.login=${SONAR_TOKEN}
                    """
                }
            }
        }

        /* ================== 5. SBOM ================== */
        stage('Generate SBOM (Syft)') {
            steps {
                sh """
                syft . -o json > sbom.json || true
                """
            }
        }

        /* ================== 6. SCA (Trivy FS) ================== */
        stage('SCA - Trivy FS Scan') {
            steps {
                sh """
                trivy fs . -o trivy-fs-report.json --format json || true
                """
            }
        }

        /* ================== 7. SECURITY GATE #1 ================== */
        stage('Security Gate #1 (SAST + SCA)') {
            steps {
                script {
                    // This input step returns the username of the approver
                    def approver = input(
                        message: "⚠ Security risks detected.\nOnly 'dhananjay' can approve.\nClick PROCEED to continue.",
                        ok: "PROCEED",
                        submitterParameter: "approvedBy"
                    )
        
                    echo "Approval clicked by: ${approver}"
        
                    if (approver != "dhananjay") {
                        error("❌ Only dhananjay can approve this stage. Approval attempted by: ${approver}")
                    }
        
                    echo "✅ Security approval granted by dhananjay."
                }
            }
        }
        
        /* ================== 8. BUILD ================== */
        stage('Build App') {
            steps {
                sh "docker build -t ${IMAGE_NAME} ."
            }
        }

        /* ================== 9. IMAGE SCAN ================== */
        stage('Trivy Image Scan') {
            steps {
                sh """
                trivy image ${IMAGE_NAME} --format json -o trivy-image-report.json || true
                """
            }
        }

        /* ================== 10. SECURITY GATE #2 ================== */
        stage('Security Gate #2 (Image Scan)') {
            steps {
                script {
        
                    // Capture the actual user who clicks PROCEED
                    def approver = input(
                        message: "⚠ CRITICAL vulnerabilities found.\nOnly 'dhananjay' can approve.\nClick PROCEED to continue.",
                        ok: "PROCEED",
                        submitterParameter: "approvedBy"   // <-- Capture approver username
                    )
        
                    echo "Approval clicked by: ${approver}"
        
                    // Verify approver is EXACTLY dhananjay
                    if (approver != "dhananjay") {
                        error("❌ Approval denied. Only 'dhananjay' can approve. Attempted by: ${approver}")
                    }
        
                    echo "✅ Approval granted by dhananjay."
                }
            }
        }




        /* ================== 11. DEPLOY ================== */
        stage('Deploy Application') {
            steps {
                sh """
                echo "Stopping any container already using port 8000..."
        
                PORT=8000
                CID=\$(docker ps -q --filter "publish=\${PORT}")
        
                if [ ! -z "\$CID" ]; then
                    echo "Port \$PORT is busy. Stopping container \$CID"
                    docker stop \$CID || true
                    docker rm \$CID || true
                fi
        
                echo "Deploying new container..."
                docker rm -f scanshield || true
                docker run -d --name scanshield -p 8000:8000 ${IMAGE_NAME}
                """
            }
        }

        /* ================== 12. DAST (OWASP ZAP) ================== */
        stage('DAST - OWASP ZAP Scan') {
            steps {
                sh """
                mkdir -p ${ZAP_REPORT_DIR}
                chmod 777 ${ZAP_REPORT_DIR}

                docker run --rm --network host \
                    -v \$(pwd)/${ZAP_REPORT_DIR}:/zap/wrk \
                    ghcr.io/zaproxy/zaproxy \
                    zap-baseline.py -t ${APP_URL} \
                    -r zap-report.html \
                    -x zap-report.xml \
                    -J zap-report.json \
                    -I || true
                """
            }
        }

        /* ================== 13. PUBLISH REPORTS ================== */
        stage('Publish Reports') {
            steps {
                publishHTML([
                    reportDir: "${ZAP_REPORT_DIR}",
                    reportFiles: 'zap-report.html',
                    reportName: 'ZAP DAST Report',
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    alwaysLinkToLastBuild : true,
                    allowMissing: true,
                ])

                publishHTML([
                    reportDir: ".",
                    reportFiles: 'trivy-fs-report.json',
                    reportName: 'Trivy FS JSON',
                    keepAll : true,
                    alwaysLinkToLastBuild : true,
                    allowMissing: true,
                    
                ])
            }
        }

    }

    /* ================== 14. POST BUILD ================== */
    post {
        always {
            script {
                archiveArtifacts artifacts: '**/*.json, **/*.xml, **/*.txt, **/*.html', fingerprint: true
            }
        }

        success {
            emailext(
                to: "dhananjaykhairnar15@gmail.com",
                subject: "SUCCESS: Build #${env.BUILD_NUMBER}",
                body: "<p>Build Completed Successfully with full DevSecOps pipeline.</p>",
                mimeType: 'text/html'
            )
        }

        failure {
            emailext(
                to: "dhananjaykhairnar15@gmail.com",
                subject: "FAILED: Build #${env.BUILD_NUMBER}",
                body: "<p>Build Failed. Check Reports.</p>",
                mimeType: 'text/html'
            )
        }
    }
}
