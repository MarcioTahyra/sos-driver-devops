
# SOS Driver - Cloud Computing & Secure DevOps

Global Solution FIAP 2026

### Integrantes
- Márcio Hitoshi Tahyra - RM552511
- Jéssica Witzler Costacurta - RM99068

## 1. Sobre o projeto

O SOS Driver é uma solução de assistência veicular sob demanda, desenvolvida para conectar motoristas que enfrentam emergências a prestadores de serviços.

O MVP implementado consiste em uma API REST para consulta de serviços e registro de solicitações de assistência veicular.

O projeto demonstra a aplicação de Cloud Computing, Infrastructure as Code, conteinerização, segurança automatizada, integração e entrega contínuas e observabilidade.

## 2. Tecnologias utilizadas

- Python 3.12
- FastAPI
- Docker e Docker Compose
- Terraform
- AWS EC2
- Docker Hub
- GitHub Actions
- Gitleaks
- Semgrep
- Trivy
- Bandit
- pip-audit
- Prometheus
- Grafana
- Pytest

## 3. Arquitetura

O código-fonte é armazenado no GitHub.

A cada push na branch main, o GitHub Actions executa testes automatizados, análises de segurança, validação do Terraform e verificação da imagem Docker.

Após a aprovação das verificações, a imagem é publicada no Docker Hub e implantada automaticamente na instância AWS EC2 por um runner self-hosted.

A API expõe métricas no endpoint /metrics, coletadas pelo Prometheus e visualizadas no Grafana.

Fluxo:

Desenvolvedor
    |
    v
GitHub
    |
    v
GitHub Actions
    |
    +-- Pytest / Bandit / pip-audit
    +-- Gitleaks
    +-- Semgrep
    +-- Terraform Validate
    +-- Docker Build / Trivy
    |
    v
Docker Hub
    |
    v
AWS EC2 - Docker - FastAPI
    |
    v
Prometheus
    |
    v
Grafana

## 4. Links

Repositorio:
https://github.com/MarcioTahyra/sos-driver-devops

API publicada:
http://32.192.180.73:8000/docs

Health check:
http://32.192.180.73:8000/health

Metricas:
http://32.192.180.73:8000/metrics

Observacao: a infraestrutura utiliza AWS Academy Sandbox. O endereco publico pode mudar ou ficar indisponivel quando o ambiente for encerrado.

## 5. Funcionalidades da API

GET /
- Informacoes gerais da API.

GET /health
- Verificacao de disponibilidade.

GET /servicos
- Consulta dos servicos de assistencia veicular.

POST /solicitacoes
- Registro de solicitacoes com tipo de servico e coordenadas geograficas.

GET /solicitacoes/{identificador}
- Consulta de solicitacao registrada.

GET /metrics
- Exposicao das metricas para o Prometheus.

As solicitacoes sao mantidas em memoria durante a execucao da aplicacao. O MVP nao possui banco de dados persistente.

## 6. Execucao local

Requisitos:
- Python 3.12
- Docker Desktop

Clonar o repositorio:

git clone https://github.com/MarcioTahyra/sos-driver-devops.git

Entrar no projeto:

cd sos-driver-devops

Construir a imagem:

docker build -t sos-driver-api:local .

Executar o container:

docker run --rm -p 127.0.0.1:8000:8000 sos-driver-api:local

Acessar:
http://localhost:8000/docs

## 7. Testes automatizados

Instalar dependencias:

python -m pip install -r requirements.txt

Instalar ferramentas de teste:

python -m pip install pytest httpx bandit pip-audit

Executar testes:

python -m pytest -v

Executar analise de seguranca:

bandit -r app -ll

Auditar dependencias:

pip-audit -r requirements.txt

## 8. DevSecOps e CI/CD

O workflow do GitHub Actions implementa:

1. Testes automatizados e verificacoes Python.
2. Gitleaks para deteccao de segredos.
3. Semgrep para analise estatica de seguranca.
4. Validacao do Terraform.
5. Construcao e analise da imagem com Trivy.
6. Publicacao da imagem aprovada no Docker Hub.
7. Deploy automatico na AWS EC2.

A publicacao e o deploy sao restritos a pushes na branch main.

Pull requests executam as verificacoes, sem publicar imagens nem realizar deploy.

Foi realizado um teste controlado de vulnerabilidade com subprocess.run e shell=True.

O Semgrep identificou o problema e bloqueou o pipeline. Apos a correcao para shell=False, as verificacoes foram aprovadas.

## 9. Infraestrutura como codigo

A pasta terraform/ contem os arquivos utilizados para provisionar a infraestrutura AWS.

Comandos principais:

terraform init

terraform fmt -check

terraform validate

terraform plan

terraform apply

O provisionamento utiliza credenciais do ambiente AWS Academy Sandbox.

Arquivos com credenciais, variaveis locais sensiveis e estado Terraform nao devem ser enviados ao repositorio.

O acesso administrativo SSH e restrito por regras de rede, sem liberacao publica irrestrita da porta 22.

## 10. Seguranca

Medidas implementadas:

- Imagem Docker baseada em Python slim.
- Execucao da aplicacao com usuario nao-root.
- Container com filesystem somente leitura.
- Remocao de capabilities Linux desnecessarias.
- Protecao contra elevacao de privilegios.
- Health check da aplicacao.
- Analise automatizada de codigo e dependencias.
- Verificacao de segredos no repositorio.
- Analise de vulnerabilidades da imagem.
- Credenciais de publicacao armazenadas em GitHub Secrets.
- Separacao entre validacao e deploy.

O runner self-hosted executa na instancia EC2. Como possui acesso ao Docker, deve ser utilizado somente em workflows confiaveis e com controles adequados sobre contribuicoes ao repositorio.

## 11. Observabilidade

O monitoramento utiliza Prometheus e Grafana.

Indicadores:

- Latencia: percentil 95 do tempo de resposta.
- Trafego: requisicoes por segundo.
- Erros: respostas HTTP 5xx por segundo.
- Saturacao: consumo de memoria do processo da API.

Foi configurado um alerta de indisponibilidade baseado na metrica up.

Durante um teste controlado, a coleta de metricas foi direcionada temporariamente para um endpoint indisponivel.

O Grafana registrou o estado Firing.

Apos restaurar a configuracao, o alerta retornou ao estado Normal.

O teste simulou uma falha de coleta de metricas, sem interromper a API hospedada na AWS.

### Executar o monitoramento localmente

Criar o arquivo monitoring/.env com:

GRAFANA_ADMIN_PASSWORD=defina_uma_senha_forte

Entrar na pasta:

cd monitoring

Iniciar os servicos:

docker compose up -d

Prometheus:
http://localhost:9090

Grafana:
http://localhost:3000

O arquivo monitoring/prometheus.yml deve apontar para o endereco atual da API publicada.

O dashboard e a regra de alerta foram configurados na interface do Grafana.

## 12. LGPD e tratamento de dados

O MVP recebe coordenadas geograficas nas solicitacoes de assistencia.

Esses dados podem constituir dados pessoais quando associados a uma pessoa identificada ou identificavel.

Atualmente, as solicitacoes sao armazenadas apenas na memoria do processo da API na instancia AWS EC2, na regiao us-east-1.

Nao ha banco de dados persistente implementado.

Para uma versao de producao, seriam necessarias medidas adicionais, como autenticacao, autorizacao, criptografia em transito, politica de retencao, minimizacao de dados e procedimentos para atendimento aos direitos dos titulares.

## 13. Responsabilidade compartilhada

AWS:
- Seguranca fisica dos datacenters.
- Infraestrutura global e camada de virtualizacao gerenciada.

Equipe do projeto:
- Configuracao da instancia EC2 e Security Groups.
- Atualizacao e protecao do sistema operacional.
- Seguranca da aplicacao e dos containers.
- Gestao de credenciais e permissoes.
- Tratamento adequado dos dados.
- Monitoramento e resposta a incidentes.

## 14. Limitacoes do MVP

- Solicitacoes armazenadas apenas em memoria.
- Ausencia de autenticacao de usuarios.
- API publicada em HTTP, sem TLS.
- Dependencia da disponibilidade do AWS Academy Sandbox.
- Prometheus e Grafana executados localmente.
- Ausencia de notificacao externa funcional no alerta demonstrativo.

Essas limitacoes devem ser tratadas antes de uma disponibilizacao em producao.

## 15. Proximos passos

- Implementar autenticacao e controle de acesso.
- Adicionar persistencia em banco de dados.
- Configurar HTTPS com dominio e certificado TLS.
- Aprimorar o isolamento do runner de deploy.
- Implementar politicas de retencao de dados.
- Adicionar monitoramento completo da infraestrutura.
- Configurar notificacoes reais de alertas.
