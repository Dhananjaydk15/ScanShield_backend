pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'sonarqube'
        // For production: store SONAR token in Jenkins credentials and use withCredentials().
        // Example: withCredentials([string(credentialsId: 'sonar-token-id', variable: 'SONAR_TOKEN')]) { ... }
        SONAR_TOKEN = 'squ_96754e8f46fcf62b692605612352ed6ca4e8bfb0'
        TRIVY_TIMEOUT = '5m'
        APP_URL = 'http://localhost:8000'   // URL ZAP & tests will hit
    }

    stages {
        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/Dhananjaydk15/ScanShield_backend.git'
            }
        }

        /* ===== SONAR SCAN ===== */
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

        /* ===== SYFT SBOM SCAN ===== */
        stage('Syft SBOM Scan') {
            steps {
                sh """
                syft . -o json > syft-report.json || true
                syft . -o table > syft-report.txt || true
                """
            }
        }

        /* ===== TRIVY SCAN (FS) ===== */
        stage('Trivy Vulnerability Scan') {
            steps {
                sh """
                echo "Creating Correct Trivy Template..."

cat << 'EOF' > trivy-report.tpl
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Trivy Vulnerability Report</title>
<style>
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; }
    th { background-color: #333; color: white; }
</style>
</head>
<body>
<h1>Trivy Vulnerability Report</h1>
{{- range .Results }}
<h2>Target: {{ .Target }}</h2>
{{- if .Vulnerabilities }}
<table>
    <tr>
        <th>Package</th>
        <th>Installed</th>
        <th>Vulnerability</th>
        <th>Severity</th>
        <th>Fixed Version</th>
        <th>Description</th>
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
{{- else }}
<p>No vulnerabilities found.</p>
{{- end }}
{{- end }}
</body>
</html>
EOF

echo "Running Trivy Scan..."
trivy fs . --scanners vuln \
    --db-repository public.ecr.aws/aquasecurity/trivy-db \
    --format template \
    --template trivy-report.tpl \
    -o trivy-report.html || true

echo "Trivy Scan Completed."
                """
            }
        }

        /* ===== BUILD ===== */
        stage('Build App') {
            steps {
                sh "docker compose build"
            }
        }

        /* ===== DEPLOY ===== */
        stage('Deploy App') {
            steps {
                sh """
                docker compose down || true
                docker compose up -d --force-recreate
                """
            }
        }

        /* ===== PUBLISH TRIVY REPORT ===== */
        stage('Publish Vulnerability Report') {
            steps {
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'trivy-report.html',
                    reportName: 'Trivy Vulnerability Report',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: true
                ])
            }
        }

        /* ===== OWASP ZAP DAST (Baseline) ===== */

stage('OWASP ZAP DAST Scan') {
    steps {
        sh """
        echo "Starting OWASP ZAP Baseline Scan..."

        # Run OWASP ZAP Baseline Scan

        docker run --rm --network host \
            --user $(id -u jenkins):$(id -g jenkins) \
            -v \$(pwd):/zap/wrk \
            ghcr.io/zaproxy/zaproxy \
            zap-baseline.py \
            -t http://localhost:8000 \
            -r zap-report.html \
            -x zap-report.xml \
            -J zap-json-report.json \
            -I || true
        

        echo "ZAP Baseline Scan Completed. Reports generated:"
        ls -l zap-report.html zap-report.xml zap-json-report.json || true
        """
    }
}


        /* ===== Publish ZAP Report ===== */
        stage('Publish ZAP Report') {
            steps {
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'zap-report.html',
                    reportName: 'OWASP ZAP DAST Report (HTML)',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: true
                ])

                // Also publish XML for other plugins (if present)
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'zap-report.xml',
                    reportName: 'OWASP ZAP DAST Report (XML)',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: true
                ])
            }
        }

        /* ===== ZAP Security Gate: fail on High/Critical ===== */
        stage('ZAP Security Gate') {
            steps {
                sh """
                echo "Evaluating ZAP findings for High/Critical alerts..."

                # If zap-json-report.json missing, treat as 0 findings
                if [ ! -f zap-json-report.json ]; then
                  echo "No zap JSON report found; skipping gate."
                  exit 0
                fi

                # Use Python to count alerts with risk "High" or "Critical"
                python3 - <<'PY'
import json,sys
f = open('zap-json-report.json')
data = json.load(f)
count = 0
# ZAP's JSON structure: data['site'] -> list of site objects each with 'alerts'
sites = data.get('site') or []
for site in sites:
    alerts = site.get('alerts') or []
    for a in alerts:
        risk = a.get('risk') or a.get('riskcode') or ''
        # risk may be "High", "Medium", etc.
        if isinstance(risk, str) and risk.lower() in ('high','critical'):
            count += 1
# Also support legacy structure: data.get('alerts')
for a in data.get('alerts', []):
    r = a.get('risk','').lower()
    if r in ('high','critical'):
        count += 1

print(count)
if count > 0:
    print(f"Found {count} High/Critical alerts. Failing the build.")
    sys.exit(2)
else:
    print("No High/Critical alerts found.")
    sys.exit(0)
PY
                """
            }
        }
    }

    post {
        always {
            // archive JSON/TXT/HTML/XML reports
            archiveArtifacts artifacts: '*.json, *.txt, *.html, *.xml', fingerprint: true
            echo "Artifacts archived."
        }

        success {
            emailext(
                to: 'dhananjaykhairnar15@gmail.com',
                subject: "SUCCESS: Build #${env.BUILD_NUMBER}",
                body: """
                <p>Hi Team,</p>
                <p>The Jenkins build <b>#${env.BUILD_NUMBER}</b> completed successfully.</p>
                <p>Vulnerability Report has been generated and archived.</p>
                <p>Regards,<br>Jenkins</p>
                """,
                mimeType: 'text/html'
            )
        }

        failure {
            emailext(
                to: 'dhananjaykhairnar15@gmail.com',
                subject: "FAILED: Build #${env.BUILD_NUMBER}",
                body: """
                <p>Hi Team,</p>
                <p>The Jenkins build <b>#${env.BUILD_NUMBER}</b> has <b>failed</b>.</p>
                <p>Please review the Jenkins console and the archived reports (Trivy / ZAP).</p>
                <p>Regards,<br>Jenkins</p>
                """,
                mimeType: 'text/html'
            )
        }
    }
}
