pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'sonarqube'
        SONAR_TOKEN = 'squ_96754e8f46fcf62b692605612352ed6ca4e8bfb0'
        IMAGE_NAME = "scanshield-backend"
        TRIVY_TIMEOUT = "5m"
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

        /* ------------------ First Approval ------------------ */
        stage('Approval Before Build') {
            steps {
                script {
                    def allowed = ['admin', 'auditor']

                    while (true) {
                        def approver = input(
                            message: "Approval required to proceed.\nOnly allowed: ${allowed}",
                            ok: "Approve",
                            submitterParameter: 'APPROVER'
                        )

                        echo "Attempted approval by: ${approver}"

                        if (allowed.contains(approver)) {
                            echo "Approved by allowed user: ${approver}"
                            break
                        } else {
                            echo "'${approver}' is NOT allowed. Waiting for correct user..."
                        }
                    }
                }
            }
        }

        /* ------------------ Second Approval ------------------ */
        stage('Approval of operational team before build') {
            steps {
                script {
                    def allowed = ['dhananjay']

                    while (true) {
                        def approver = input(
                            message: "Operational Approval required.\nOnly allowed: ${allowed}",
                            ok: "Approve",
                            submitterParameter: 'APPROVER'
                        )

                        echo "Attempted approval by: ${approver}"

                        if (allowed.contains(approver)) {
                            echo "Approved by allowed user: ${approver}"
                            break
                        } else {
                            echo "'${approver}' is NOT allowed. Waiting again..."
                        }
                    }
                }
            }
        }

        /* ------------------ Install Syft & Trivy ------------------ */
        stage('Install Syft & Trivy') {
            steps {
                sh '''
                mkdir -p reports

                # Install Syft if missing
                if ! command -v syft >/dev/null; then
                  echo "Installing Syft..."
                  wget -qO- https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
                fi

                # Install Trivy if missing
                if ! command -v trivy >/dev/null; then
                  echo "Installing Trivy..."
                  apt-get update -y
                  apt-get install -y wget gnupg
                  wget -q https://aquasecurity.github.io/trivy-repo/deb/public.key -O- | apt-key add -
                  echo "deb https://aquasecurity.github.io/trivy-repo/deb stable main" | tee /etc/apt/sources.list.d/trivy.list
                  apt-get update
                  apt-get install -y trivy
                fi
                '''
            }
        }

        /* ------------------ Build Docker Image ------------------ */
        stage('Build App') {
            steps {
                sh "docker compose build"
            }
        }

        /* ------------------ SBOM (Syft) ------------------ */
        stage('Generate SBOM (Syft)') {
            steps {
                sh '''
                syft . -o json > reports/sbom.json
                syft . -o cyclonedx-json > reports/sbom-cyclonedx.json
                '''
            }
        }

        /* ------------------ Trivy FS Scan ------------------ */
        stage('Trivy FS Scan') {
            steps {
                sh '''
                trivy fs . \
                    --scanners vuln,secret,config \
                    --format json \
                    --timeout ${TRIVY_TIMEOUT} \
                    --output reports/trivy-fs.json || true
                '''
            }
        }

        /* ------------------ Trivy Image Scan ------------------ */
        stage('Trivy Image Scan') {
            steps {
                sh '''
                trivy image ${IMAGE_NAME} \
                    --severity HIGH,CRITICAL \
                    --timeout ${TRIVY_TIMEOUT} \
                    --format json \
                    --output reports/trivy-image.json \
                    --exit-code 1 || true
                '''
            }
        }

        /* ------------------ Deploy App ------------------ */
        stage('Deploy App') {
            steps {
                sh '''
                docker compose down
                docker compose up -d --force-recreate
                '''
            }
        }

        /* ------------------ Archive Security Reports ------------------ */
        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'reports/*', fingerprint: true
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
