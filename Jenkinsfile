pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'sonarqube'
        SONAR_TOKEN = credentials('sonar-token')   // ✔ Secure token storage
        TRIVY_TIMEOUT = '5m'
        APP_URL = 'http://localhost:8000'
        ZAP_REPORT_DIR = 'zap-reports'
    }

    stages {

        /* ================== CLONE ================== */
        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/Dhananjaydk15/ScanShield_backend.git'
            }
        }

        /* ================== SAST (SONAR) ================== */
        stage('SonarQube Analysis') {
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

        /* ================== SBOM (SYFT) ================== */
        stage('Syft SBOM Scan') {
            steps {
                sh """
                syft . -o json > syft-report.json || true
                syft . -o table > syft-report.txt || true
                """
            }
        }

        /* ================== SCA (TRIVY FS) ================== */
        stage('Trivy Vulnerability Scan') {
            steps {
                sh """
                echo "Creating Trivy HTML Template..."

cat << 'EOF' > trivy-report.tpl
<!DOCTYPE html>
<html>
<head>
<title>Trivy Vulnerability Report</title>
<style>
table {border-collapse:collapse;width:100%;}
th,td {border:1px solid #ddd;padding:8px;}
th {background:#333;color:white;}
</style>
</head>
<body>
<h1>Trivy Vulnerability Report</h1>
{{- range .Results }}
<h2>Target: {{ .Target }}</h2>
{{- if .Vulnerabilities }}
<table>
<tr>
<th>Package</th><th>Installed</th><th>Vulnerability</th><th>Severity</th><th>Fixed</th><th>Description</th>
</tr>
{{- range .Vulnerabilities }}
<tr>
<td>{{ .PkgName }}</td>
<td>{{ .InstalledVersion }}</td>
<td>{{ .VulnerabilityID }}</td>
<td>{{ .Severity }}</td>
<td>{{ .FixedVersion }}</td>
<td>{{ .Description }}</td>
</tr>
{{- end }}
</table>
{{ else }}<p>No vulnerabilities.</p>{{ end }}
{{- end }}
</body>
</html>
EOF

                echo "Running Trivy Scan..."
                trivy fs . --scanners vuln \
                    --format template \
                    --template trivy-report.tpl \
                    -o trivy-report.html || true
                """
            }
        }

        /* ================== BUILD ================== */
        stage('Build App') {
            steps {
                sh "docker compose build"
            }
        }

        /* ================== DEPLOY ================== */
        stage('Deploy App') {
            steps {
                sh """
                docker compose down || true
                docker compose up -d --force-recreate
                """
            }
        }

        /* ================== PUBLISH TRIVY REPORT ================== */
        stage('Publish Trivy Report') {
            steps {
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'trivy-report.html',
                    reportName: 'Trivy Vulnerability Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true
                ])
            }
        }

        /* ================== DAST (OWASP ZAP) ================== */
        stage('OWASP ZAP DAST Scan') {
            steps {
                sh """
                echo "Preparing ZAP writable directory..."
                mkdir -p ${ZAP_REPORT_DIR}
                chmod 777 ${ZAP_REPORT_DIR}

                echo "Running OWASP ZAP Baseline Scan..."

                docker run --rm --network host \
                    -v \$(pwd)/${ZAP_REPORT_DIR}:/zap/wrk \
                    ghcr.io/zaproxy/zaproxy \
                    zap-baseline.py \
                    -t ${APP_URL} \
                    -r zap-report.html \
                    -x zap-report.xml \
                    -J zap-json-report.json \
                    -I || true

                echo "ZAP Scan Completed. Files:"
                ls -l ${ZAP_REPORT_DIR}
                """
            }
        }

        /* ================== PUBLISH ZAP REPORTS ================== */
        stage('Publish ZAP Reports') {
            steps {
                publishHTML([
                    reportDir: "${ZAP_REPORT_DIR}",
                    reportFiles: 'zap-report.html',
                    reportName: 'OWASP ZAP DAST Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true
                ])
            }
        }

        /* ================== SECURITY GATE ================== */
        stage('ZAP Security Gate') {
            steps {
                sh """
                echo "Checking ZAP report for HIGH/CRITICAL alerts..."

                if [ ! -f ${ZAP_REPORT_DIR}/zap-json-report.json ]; then
                  echo "No ZAP JSON report found. Skipping security gate."
                  exit 0
                fi

                python3 - <<'PY'
import json, sys
path = "${ZAP_REPORT_DIR}/zap-json-report.json"
data = json.load(open(path))
count = 0

for site in data.get("site", []):
    for a in site.get("alerts", []):
        risk = a.get("risk", "").lower()
        if risk in ["high", "critical"]:
            count += 1

print("High/Critical findings:", count)
sys.exit(2 if count > 0 else 0)
PY
                """
            }
        }
    }

    /* ================== POST BUILD ================== */
    post {
        always {
            archiveArtifacts artifacts: '**/*.json, **/*.txt, **/*.html, **/*.xml', fingerprint: true
        }

        success {
            emailext(
                to: 'dhananjaykhairnar15@gmail.com',
                subject: "SUCCESS: Build #${env.BUILD_NUMBER}",
                body: "<p>Build succeeded. Reports generated (Trivy + ZAP).</p>",
                mimeType: 'text/html'
            )
        }

        failure {
            emailext(
                to: 'dhananjaykhairnar15@gmail.com',
                subject: "FAILED: Build #${env.BUILD_NUMBER}",
                body: "<p>Build failed. Check reports for details.</p>",
                mimeType: 'text/html'
            )
        }
    }
}
