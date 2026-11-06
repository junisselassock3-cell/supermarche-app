# Image Jenkins avec Python (pour les tests) et le client Docker (pour le build)
FROM jenkins/jenkins:lts-jdk21

USER root

# Client Docker + buildx copiés depuis l'image officielle (pas besoin d'apt pour ça)
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker:27-cli /usr/local/libexec/docker/cli-plugins /usr/local/libexec/docker/cli-plugins

# Python pour lancer pytest. Passage d'apt en HTTPS : le réseau du bureau bloque le HTTP.
RUN sed -i 's|http://|https://|g' /etc/apt/sources.list.d/*.sources 2>/dev/null || true \
 && apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv \
 && rm -rf /var/lib/apt/lists/*

USER jenkins
