#!/usr/bin/env python3
"""
Ollama Connection Diagnostic Script for TopicLens

This script diagnoses Ollama connection issues and helps identify
the correct configuration for the deep research feature.

Usage: python diagnose_ollama.py
"""

import httpx
import json
import os
import sys
import time
from pathlib import Path

# Test URLs in order of likelihood
OLLAMA_TEST_URLS = [
    "http://localhost:11434",
    "http://127.0.0.1:11434",
    "http://host.docker.internal:11434",
    "http://0.0.0.0:11434"
]

# Test model from current configuration
TEST_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
BACKUP_MODELS = ["llama3.2", "llama3.1", "mistral", "qwen"]

def test_ollama_connection(url: str, timeout: float = 10.0) -> dict:
    """Test connection to Ollama server at given URL."""
    print(f"[TEST] Testing Ollama server at: {url}")

    result = {
        "url": url,
        "server_accessible": False,
        "models_available": [],
        "test_model_works": False,
        "error": None,
        "response_time": None
    }

    try:
        start_time = time.time()

        # Test 1: Check if server is running
        response = httpx.get(f"{url}/api/tags", timeout=timeout)
        result["response_time"] = round(time.time() - start_time, 2)

        if response.status_code == 200:
            result["server_accessible"] = True

            # Parse available models
            try:
                data = response.json()
                models = data.get("models", [])
                result["models_available"] = [model.get("name", "") for model in models]
                print(f"[OK] Server accessible! Found {len(models)} models")

                # Test 2: Check if our target model is available
                model_names = result["models_available"]
                if TEST_MODEL in model_names:
                    print(f"[OK] Target model '{TEST_MODEL}' is available")

                    # Test 3: Try generating text with the model
                    test_result = test_model_generation(url, TEST_MODEL, timeout)
                    result["test_model_works"] = test_result["success"]
                    if not test_result["success"]:
                        result["error"] = test_result["error"]
                else:
                    result["error"] = f"Target model '{TEST_MODEL}' not found in available models"
                    print(f"[WARN] Target model '{TEST_MODEL}' not available")
                    print(f"[INFO] Available models: {', '.join(model_names)}")

                    # Try backup models
                    for backup_model in BACKUP_MODELS:
                        if backup_model in model_names:
                            print(f"[TEST] Trying backup model: {backup_model}")
                            test_result = test_model_generation(url, backup_model, timeout)
                            if test_result["success"]:
                                result["test_model_works"] = True
                                result["working_model"] = backup_model
                                print(f"[OK] Backup model '{backup_model}' works!")
                                break

            except json.JSONDecodeError as e:
                result["error"] = f"Invalid JSON response: {e}"
        else:
            result["error"] = f"Server returned status {response.status_code}"

    except httpx.ConnectError:
        result["error"] = "Connection refused - Ollama server not running"
    except httpx.TimeoutException:
        result["error"] = f"Connection timeout after {timeout}s"
    except Exception as e:
        result["error"] = str(e)

    return result

def test_model_generation(url: str, model: str, timeout: float = 30.0) -> dict:
    """Test if a model can generate text."""
    try:
        response = httpx.post(
            f"{url}/api/generate",
            json={
                "model": model,
                "prompt": "Reply with just: OLLAMA_TEST_SUCCESS",
                "stream": False,
                "options": {"temperature": 0.1, "num_ctx": 512}
            },
            timeout=timeout
        )

        if response.status_code == 200:
            data = response.json()
            generated_text = data.get("response", "").strip()

            if "OLLAMA_TEST_SUCCESS" in generated_text:
                return {"success": True, "response": generated_text}
            else:
                return {"success": False, "error": f"Unexpected response: {generated_text}"}
        else:
            return {"success": False, "error": f"Generation failed with status {response.status_code}"}

    except Exception as e:
        return {"success": False, "error": str(e)}

def diagnose_environment():
    """Diagnose the current environment and configuration."""
    print("\n" + "="*60)
    print("TOPICLENS OLLAMA DIAGNOSTIC TOOL")
    print("="*60)

    # Check environment variables
    print("\n[INFO] Current Environment Configuration:")
    print(f"OLLAMA_URL: {os.getenv('OLLAMA_URL', 'Not set (using default)')}")
    print(f"OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'Not set (using default)')}")
    print(f"Target model: {TEST_MODEL}")

    # Check if running in Docker
    is_docker = Path('/.dockerenv').exists()
    print(f"Docker environment: {'Yes' if is_docker else 'No'}")

    print(f"\n[SCAN] Testing {len(OLLAMA_TEST_URLS)} potential Ollama URLs...")

    results = []
    working_configs = []

    for url in OLLAMA_TEST_URLS:
        result = test_ollama_connection(url)
        results.append(result)

        if result["server_accessible"] and result["test_model_works"]:
            working_model = result.get("working_model", TEST_MODEL)
            working_configs.append({
                "url": url,
                "model": working_model,
                "response_time": result["response_time"]
            })

        print()  # Add spacing between tests

    # Generate report
    print("\n" + "="*60)
    print("DIAGNOSTIC RESULTS")
    print("="*60)

    if working_configs:
        print(f"[SUCCESS] Found {len(working_configs)} working configuration(s)!")

        # Recommend best configuration
        best_config = min(working_configs, key=lambda x: x["response_time"])
        print(f"\n[RECOMMEND] Best configuration:")
        print(f"  OLLAMA_URL = {best_config['url']}")
        print(f"  OLLAMA_MODEL = {best_config['model']}")
        print(f"  Response time: {best_config['response_time']}s")

        # Generate environment file
        env_content = f"""# Ollama Configuration for TopicLens
# Generated by diagnose_ollama.py

OLLAMA_URL={best_config['url']}
OLLAMA_MODEL={best_config['model']}
"""

        try:
            with open(".env.ollama", "w") as f:
                f.write(env_content)
            print(f"\n[SAVE] Configuration saved to .env.ollama")
            print("Add these to your environment or .env file")
        except Exception as e:
            print(f"\n[ERROR] Could not save configuration: {e}")

        # Show all working configs
        if len(working_configs) > 1:
            print(f"\n[INFO] All working configurations:")
            for i, config in enumerate(working_configs, 1):
                print(f"  {i}. {config['url']} with {config['model']} ({config['response_time']}s)")

    else:
        print("[ERROR] No working Ollama configurations found!")
        print("\n[TROUBLESHOOT] Possible issues:")
        print("1. Ollama is not installed or running")
        print("2. Ollama is running on a different port")
        print("3. Required model is not installed")
        print("4. Firewall is blocking connections")

        print(f"\n[FIX] To fix this:")
        print("1. Install Ollama: https://ollama.ai/")
        print("2. Start Ollama service: 'ollama serve'")
        print(f"3. Pull the model: 'ollama pull {TEST_MODEL}'")
        print("4. Or try a different model like: 'ollama pull llama3.2'")

    # Show detailed results for debugging
    print(f"\n[DEBUG] Detailed test results:")
    for result in results:
        print(f"\n  URL: {result['url']}")
        print(f"  Server accessible: {result['server_accessible']}")
        print(f"  Models available: {len(result['models_available'])}")
        print(f"  Test model works: {result['test_model_works']}")
        if result['error']:
            print(f"  Error: {result['error']}")
        if result['response_time']:
            print(f"  Response time: {result['response_time']}s")

    return working_configs

def main():
    """Main function."""
    working_configs = diagnose_environment()

    if working_configs:
        print("\n[NEXT] You can now:")
        print("1. Update your environment variables with the recommended configuration")
        print("2. Restart your TopicLens backend with the new configuration")
        print("3. Test the deep analysis feature")
        return True
    else:
        print("\n[NEXT] Fix the Ollama setup first, then run this script again")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)