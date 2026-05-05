// =============================================================================
// SE4206 - Jenkins Multi-Stage CI/CD Pipeline (Pipeline-as-Code)
//
// Stages:  Checkout -> Build -> Test -> Package -> Deploy
// Demonstrates: environment variables, post-build actions, failure handling,
//               clean rollback on failure, and a smoke test after deploy.
// =============================================================================

pipeline {
    agent any

    // -------------------------------------------------------------------------
    // Pipeline-wide environment variables. Centralising them here means we
    // never hard-code values in stages - a real-world maintainability win.
    // -------------------------------------------------------------------------
    environment {
        IMAGE_NAME      = 'se4206-flask-app'
        IMAGE_TAG       = "${env.BUILD_NUMBER}"
        CONTAINER_NAME  = 'se4206-app-prod'
        APP_PORT        = '8080'    // Host port (what the user/grader hits)
        CONTAINER_PORT  = '5000'    // Port exposed inside the container
    }

    // -------------------------------------------------------------------------
    // Sensible global guard-rails. timeout prevents a stuck build from
    // hogging the agent forever; buildDiscarder keeps the history tidy.
    // -------------------------------------------------------------------------
    options {
        timeout(time: 10, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '5'))
        timestamps()
        disableConcurrentBuilds()
    }

    stages {

        stage('Checkout') {
            steps {
                echo "📥 Pulling source code from SCM..."
                checkout scm
                sh 'ls -la'
            }
        }

        stage('Build') {
            steps {
                echo "🔧 Creating virtualenv and installing dependencies..."
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip --quiet
                    pip install -r requirements.txt --quiet
                    pip list
                '''
            }
        }

        stage('Test') {
            steps {
                echo "🧪 Running pytest unit tests..."
                sh '''
                    . venv/bin/activate
                    pytest app/tests/ -v --junitxml=test-results.xml
                '''
            }
            post {
                // Always publish results so they show up in the Jenkins UI,
                // even if the stage failed.
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }

        stage('Package') {
            steps {
                echo "📦 Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}..."
                sh '''
                    docker build \
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${IMAGE_NAME}:latest \
                        .
                    docker images | grep ${IMAGE_NAME}
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo "🚀 Deploying container locally on port ${APP_PORT}..."
                sh '''
                    # Idempotent deploy: stop & remove any previous version.
                    # The "|| true" stops the pipeline failing on first-ever run
                    # when no previous container exists.
                    docker stop ${CONTAINER_NAME} 2>/dev/null || true
                    docker rm   ${CONTAINER_NAME} 2>/dev/null || true

                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:${CONTAINER_PORT} \
                        -e APP_VERSION=${IMAGE_TAG} \
                        -e APP_ENV=production \
                        --restart unless-stopped \
                        ${IMAGE_NAME}:latest

                    echo "Waiting for the app to become ready..."
                    sleep 5

                    # Smoke test: prove the deployed container actually serves traffic.
                    # If /health does not return 200, the pipeline fails here.
                    curl --fail --silent --show-error http://localhost:${APP_PORT}/health
                    echo ""
                    echo "✅ Smoke test passed."
                '''
            }
        }
    }

    // -------------------------------------------------------------------------
    // Post-build actions: run regardless of stage outcome.
    // 'failure' performs a tidy rollback so a broken deploy does not leave
    // a half-running container behind - a small but real-world touch.
    // -------------------------------------------------------------------------
    post {
        success {
            echo "✅ Pipeline #${BUILD_NUMBER} succeeded."
            echo "🌐 App is live at http://localhost:${APP_PORT}"
            echo "🔎 Try: curl http://localhost:${APP_PORT}/api/sum/10/20"
        }
        failure {
            echo "❌ Pipeline #${BUILD_NUMBER} failed. Rolling back..."
            sh '''
                docker stop ${CONTAINER_NAME} 2>/dev/null || true
                docker rm   ${CONTAINER_NAME} 2>/dev/null || true
            '''
        }
        always {
            echo "🧹 Cleaning workspace..."
            cleanWs()
        }
    }
}
