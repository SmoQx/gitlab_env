
# 🛠️ CI/CD Demo – GitLab + Docker

W pełni konteneryzowane środowisko **GitLab Community Edition** z samozarejestrowanym Docker Runnerem oraz panelem **Portainer**.
Uruchomisz je jednym poleceniem, by ćwiczyć zarządzanie pipeline’ami, testy jednostkowe i automatyczny deployment.

---

## Spis treści
1. [O projekcie](#o-projekcie)
2. [Stos technologiczny](#stos-technologiczny)
3. [Wymagania](#wymagania)
4. [Instalacja](#instalacja)
5. [Struktura kontenerów](#struktura-kontenerów)
6. [Pipeline CI/CD](#pipeline-cicd)
7. [Zarządzanie](#zarządzanie)
8. [Rejestracja GitLab Runnera](#rejestracja-gitlab-runnera)
9. [Przydatne komendy](#przydatne-komendy)
10. [Licencja](#licencja)

---

## O projekcie

Projekt demonstruje **kompletny cykl życia oprogramowania** (lint → test → build → sast → dast → deploy) w GitLab CI/CD.
Po pierwszym uruchomieniu otrzymujesz:

* własny serwer **GitLab CE** (z prekonfigurowanym użytkownikiem `root`);
* kontener **GitLab Runner** w trybie *Docker‑in‑Docker*;
* panel **Portainer** do graficznego podglądu kontenerów;
* przykładową aplikację Python (`projekt_automatyzacja`) z testami `pytest`;
* rozszerzony pipeline z etapami **SAST** (Semgrep) i **DAST** (OWASP ZAP).

---

## Stos technologiczny

| Warstwa        | Technologia                     |
| -------------- | ------------------------------- |
| VCS + CI/CD    | GitLab CE 16.10                 |
| Runner         | GitLab Runner (Docker executor) |
| Orkiestracja   | docker‑compose v2               |
| Aplikacja demo | Python 3.12, customtkinter      |
| Testy          | pytest, coverage.py             |
| Linter         | flake8                          |
| Zarządzanie    | Portainer CE 2.20               |

---

## Wymagania

* **Docker ≥ 24.0** oraz **docker‑compose v2**
* min. **4 GB RAM** i **10 GB wolnego miejsca**
* Wolne porty: `80`, `443`, `8929`, `9090`

---

## Instalacja

```bash
# 1. Klonuj repo
git clone https://example.com/user/gitlab_env.git
cd gitlab_env

# 2. Podnieś środowisko (pierwszy start ~5‑10 min)
docker compose up -d

# 3. Zaloguj się do GitLab
#    URL: http://localhost/
#    Login: root | Hasło: patrz secrets/.initial_password
```

> 💡 **Tip:** Podgląd logów `docker compose logs -f gitlab`.

---

## Struktura kontenerów

| Kontener | Obraz | Porty | Rola |
| -------- | ----- | ----- | ---- |
| `gitlab` | `gitlab/gitlab-ce:16.10.6-ce.0` | 80, 443, 8929 | Repo + serwer CI |
| `gitlab-runner` | `gitlab/gitlab-runner:alpine-v16.10.0` | — | Wykonuje joby CI |
| `portainer` | `portainer/portainer-ce:2.20` | 9090 | UI Docker |
| `user_adder` | custom Python                 | — | Ustawia hasło root |
| `runner_ip_changer` | custom Python          | — | Aktualizuje Runner |

Pełny `docker-compose.yaml` znajdziesz w [`/docker-compose.yaml`](./docker-compose.yaml).

---

## Pipeline CI/CD

```mermaid
graph LR
A[Push] --> B[Lint]
B --> C[Testy]
C --> D[Build]
D --> E[Deploy]
```

Etapy domyślnego pipeline:

1. **Lint** – `flake8`
2. **Testy** – `pytest` + raport pokrycia HTML
3. **Build** – budowa obrazu Docker
4. **Deploy** – `docker compose up --build`

---

## Zarządzanie

* **Portainer:** <http://localhost:9090>
* **Runner logs:** `docker compose logs -f gitlab-runner`
* **Zmiana hasła root:** `docker exec -it gitlab gitlab-rake "gitlab:password:reset[root]"`

---

## Rejestracja GitLab Runnera

Po pierwszym uruchomieniu środowiska zarejestruj własnego runnera:

1. **Zaloguj się do GitLab**  
   - URL: `http://localhost/`  
   - Użytkownik: `usr`  
   - Hasło: `123password`

2. **Przejdź do swojego projektu**  
   Wybierz projekt, w którym chcesz uruchamiać pipeline’y.

3. **Otwórz ustawienia runnerów**  
   W bocznym menu GitLab wybierz **CI/CD → Runners**.

4. **Skopiuj token rejestracyjny**  
   W sekcji **Set up a specific Runner manually** kliknij **Register a new runner** i skopiuj wyświetlony **registration token**.

5. **Wstaw token do konfiguracji**  
   Otwórz plik `gitlab-runner-config/config.toml` i podmień linię z tokenem:
   ```toml
   [[runners]]
    name = "gitlab-runner"
    url = "http://gitlab/"
    id = 46
     # zastąp poniższy placeholder swoim tokenem
    token = "TU_WSTAW_SWÓJ_TOKEN"
    token_obtained_at = 2025-04-07T14:27:06Z
    token_expires_at = 0001-01-01T00:00:00Z
    executor = "docker"

6. Zrestartuj runnera

  `docker compose restart gitlab-runner`

7. Zweryfikuj status
   Nowy runner powinien pojawić się w panelu GitLab jako **active**.

---

## Przydatne komendy

| Cel | Komenda |
| --- | ------- |
| zatrzymanie środowiska | `docker compose down` |
| aktualizacja obrazów   | `docker compose pull && docker compose up -d --build` |
| przebudowa runnera     | `docker compose restart gitlab-runner` |
| podgląd pokrycia testów | Otwórz `htmlcov/index.html` w artefaktach pipeline |

---
