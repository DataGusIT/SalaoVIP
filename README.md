# Salão VIP - Sistema de Gestão e Agendamento

> Sistema web completo para modernizar o atendimento de barbearias e salões de beleza, conectando clientes e profissionais de forma eficiente com um agendamento inteligente.

[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-blue)](https://github.com/seu-usuario/salao-vip)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-Framework-092E20)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

## Sobre o Projeto

O **Salão VIP** é uma aplicação web Full-Stack desenvolvida para otimizar a gestão e o agendamento em barbearias e salões de beleza. A plataforma resolve problemas críticos como conflitos de horário e a dificuldade de gerenciar a disponibilidade dos profissionais, oferecendo uma experiência fluida tanto para o cliente quanto para o estabelecimento.

Construído com Python e Django, o sistema possui uma lógica de agendamento avançada que calcula horários disponíveis em tempo real, considerando a agenda, folgas e duração de cada serviço, garantindo que não ocorra duplo agendamento (*overbooking*).

## 🖼️ Demonstração Visual

| Página Inicial | Dashboard do Profissional | Gestão de Disponibilidade |
| :---: | :---: | :---: |
| <img alt="Página Inicial" src="https://github.com/user-attachments/assets/5c37d46d-a5a7-41fb-b744-e21ac5cfb29f" /> | <img alt="Dashboard do Profissional" src="https://github.com/user-attachments/assets/07a64213-19bb-4c48-a867-08290571a9b3" /> | <img alt="Gestão de Disponibilidade" src="https://github.com/user-attachments/assets/6956e4c1-eeec-4e60-afb3-9e690a7b0d8b" /> |
| **Perfil do Usuário** | **Agendamento para Clientes** | **Histórico de Visitas** |
| <img alt="Perfil do Usuário" src="https://github.com/user-attachments/assets/86288918-dc42-41ee-bd7c-2a312a090b78" /> | <img alt="Tela de Agendamento" src="https://github.com/user-attachments/assets/5ffea7cd-b9a6-4f2d-b612-9bb88e8e0f93" /> | <img alt="Histórico de Visitas" src="https://github.com/user-attachments/assets/bbc44a8a-d28e-4792-9d84-ad3302f550e2" /> |

## ✨ Funcionalidades

### 🗓️ Agendamento Inteligente e Gestão
-   **Disponibilidade em Tempo Real:** Um algoritmo, exposto via API, calcula e exibe apenas os horários livres, considerando a duração dos serviços, folgas e intervalos de almoço dos profissionais.
-   **Prevenção de Conflitos:** O sistema impede *overbooking* (duplo agendamento) e valida os horários para garantir que estejam dentro do expediente comercial.

### 👤 Portais de Usuário com Múltiplos Atores
-   **Portal do Cliente:**
    -   Agendamento rápido e intuitivo.
    -   Perfil personalizável e histórico completo de visitas e serviços realizados.
-   **Portal do Profissional:**
    -   **Dashboard com KPIs:** Visualização de métricas de performance, como faturamento e total de atendimentos.
    -   **Agenda Interativa:** Gerenciamento da agenda diária com status de cada atendimento (confirmado, finalizado, etc.).
    -   **Prontuário Técnico:** Um sistema de notas internas para registrar detalhes técnicos sobre cada cliente (ex: tipo de corte, produtos usados), garantindo um atendimento personalizado.
-   **Portal do Administrador:**
    -   Controle total sobre serviços, profissionais, horários e configurações do sistema.

### ✨ Experiência do Usuário (UX/UI)
-   **Design Mobile-First:** Interface totalmente responsiva, garantindo uma ótima experiência em qualquer dispositivo.
-   **Notificações Interativas:** Uso de *Toasts* para fornecer feedback instantâneo ao usuário sobre suas ações (ex: agendamento confirmado).
-   **Interface Moderna:** Construída com Bootstrap 5 para um visual limpo e profissional.

## Tecnologias

### Backend
-   **Python 3**
-   **Django 5**

### Frontend
-   **HTML5** e **CSS3**
-   **Bootstrap 5**
-   **JavaScript (Fetch API)** - Para comunicação assíncrona com a API de agendamento.

### Banco de Dados
-   **SQLite** (Desenvolvimento)
-   **PostgreSQL** (Produção, via Supabase)

### Deploy
-   **Render** (para a aplicação Django)
-   **Supabase** (para o banco de dados PostgreSQL)

## Pré-requisitos

-   Python 3.9 ou superior
-   Pip (gerenciador de pacotes do Python)

## Instalação e Uso

1.  **Clone o repositório**
    ```bash
    git clone https://github.com/seu-usuario/salao-vip.git
    cd salao-vip
    ```

2.  **Crie e ative um ambiente virtual**
    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instale as dependências**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Aplique as migrações do banco de dados**
    ```bash
    python manage.py migrate
    ```

5.  **Crie um superusuário (Admin)**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Execute a aplicação**
    ```bash
    python manage.py runserver
    ```
    Acesse o sistema em `http://127.0.0.1:8000`.

## Suporte e Contato

-   **Email**: [g.moreno.souza05@gmail.com](mailto:g.moreno.souza05@gmail.com)
-   **LinkedIn**: [Gustavo Moreno](https://www.linkedin.com/in/gustavo-moreno-8a925b26a/)

## Licença

Este projeto está licenciado sob uma Licença Proprietária.

**Uso Restrito**: Este software é de propriedade exclusiva do autor. Uso comercial ou redistribuição requer autorização expressa.

---

<div align="center">
  Desenvolvido por Gustavo Moreno
  <br><br>
  <a href="https://www.linkedin.com/in/gustavo-moreno-8a925b26a/" target-blank">
    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="24" alt="LinkedIn"/>
  </a>
</div>
