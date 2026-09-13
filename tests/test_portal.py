import os
import subprocess
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def test_mkdocs_config_validity():
    cfg_path = os.path.join(BASE_DIR, "mkdocs.yml")
    assert os.path.exists(cfg_path)
    with open(cfg_path, "r", encoding="utf-8") as f:
        data = yaml.unsafe_load(f)
    assert data["site_name"] == "Enterprise Platform Delivery & Reliability Portal"
    assert data["theme"]["name"] == "material"
    assert "mermaid" in str(data)

def test_deploy_workflow_exists():
    wf_path = os.path.join(BASE_DIR, ".github", "workflows", "deploy-portal.yml")
    assert os.path.exists(wf_path)
    with open(wf_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "actions/deploy-pages" in content
    assert "mkdocs build --strict" in content

def test_mkdocs_strict_build():
    res = subprocess.run(["python", "-m", "mkdocs", "build", "--strict"], cwd=BASE_DIR, capture_output=True, text=True)
    assert res.returncode == 0, f"MkDocs strict build failed: {res.stderr}"
    assert os.path.exists(os.path.join(BASE_DIR, "site", "index.html"))
