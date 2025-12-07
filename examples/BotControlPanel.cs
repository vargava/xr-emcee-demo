using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using System;

/// <summary>
/// Meta Quest Control Panel for Friendly Host Bot
/// 
/// Setup Instructions:
/// 1. Create a Canvas in your Unity scene
/// 2. Add this script to an empty GameObject
/// 3. In Inspector, assign:
///    - All the UI dropdowns and buttons
///    - Set serverURL to your Docker host IP (e.g., "http://192.168.1.100:5000")
/// 4. Build and deploy to Quest
/// </summary>
public class BotControlPanel : MonoBehaviour
{
    [Header("Server Configuration")]
    [Tooltip("Your Docker host IP and port (e.g., http://192.168.1.100:5000)")]
    public string serverURL = "http://192.168.1.100:5000";
    
    [Header("UI Elements")]
    public TMP_Dropdown personalityDropdown;
    public TMP_Dropdown toneDropdown;
    public TMP_Dropdown sceneDropdown;
    public TMP_InputField customSceneInput;
    public Button initializeButton;
    public Button resetButton;
    public TMP_Text statusText;
    public TMP_Text responseText;
    
    [Header("Test Chat (Optional)")]
    public TMP_InputField chatInputField;
    public Button sendChatButton;
    
    private Dictionary<string, object> availableOptions;
    
    void Start()
    {
        // Setup button listeners
        initializeButton.onClick.AddListener(InitializeBot);
        resetButton.onClick.AddListener(ResetConversation);
        
        if (sendChatButton != null)
            sendChatButton.onClick.AddListener(SendTestMessage);
        
        // Load available options from server
        StartCoroutine(LoadAvailableOptions());
        
        // Check server health
        StartCoroutine(CheckHealth());
    }
    
    IEnumerator CheckHealth()
    {
        statusText.text = "Checking connection...";
        
        using (UnityWebRequest request = UnityWebRequest.Get(serverURL + "/health"))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                var response = JsonUtility.FromJson<HealthResponse>(request.downloadHandler.text);
                statusText.text = $"✅ Connected | Bot: {(response.bot_initialized ? "Ready" : "Not Init")}";
            }
            else
            {
                statusText.text = $"❌ Cannot connect to {serverURL}";
                Debug.LogError($"Health check failed: {request.error}");
            }
        }
    }
    
    IEnumerator LoadAvailableOptions()
    {
        using (UnityWebRequest request = UnityWebRequest.Get(serverURL + "/available_options"))
        {
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                var optionsJson = request.downloadHandler.text;
                var options = JsonUtility.FromJson<AvailableOptions>(optionsJson);
                
                // Populate personality dropdown
                personalityDropdown.ClearOptions();
                personalityDropdown.AddOptions(new List<string>(options.personalities));
                
                // Populate tone dropdown
                toneDropdown.ClearOptions();
                toneDropdown.AddOptions(new List<string>(options.tones));
                
                // Populate scene dropdown
                sceneDropdown.ClearOptions();
                sceneDropdown.AddOptions(new List<string>(options.scenes));
                
                Debug.Log("✅ Loaded available options");
            }
            else
            {
                Debug.LogError($"Failed to load options: {request.error}");
            }
        }
    }
    
    public void InitializeBot()
    {
        string personality = personalityDropdown.options[personalityDropdown.value].text;
        string tone = toneDropdown.options[toneDropdown.value].text;
        string scene = sceneDropdown.options[sceneDropdown.value].text;
        string customScene = customSceneInput.text;
        
        StartCoroutine(InitializeBotRequest(personality, tone, scene, customScene));
    }
    
    IEnumerator InitializeBotRequest(string personality, string tone, string scene, string customScene)
    {
        statusText.text = "Initializing bot...";
        
        // Create JSON payload
        var config = new InitializeConfig
        {
            personality = personality,
            tone = tone,
            scene = scene,
            custom_scene = customScene
        };
        
        string jsonData = JsonUtility.ToJson(config);
        
        using (UnityWebRequest request = new UnityWebRequest(serverURL + "/initialize", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                var response = JsonUtility.FromJson<StandardResponse>(request.downloadHandler.text);
                statusText.text = $"✅ {response.message}";
                Debug.Log($"Bot initialized: {personality}/{tone}/{scene}");
            }
            else
            {
                statusText.text = $"❌ Failed: {request.error}";
                Debug.LogError($"Initialize failed: {request.error}");
            }
        }
    }
    
    public void ResetConversation()
    {
        StartCoroutine(ResetConversationRequest());
    }
    
    IEnumerator ResetConversationRequest()
    {
        statusText.text = "Resetting for new visitor...";
        
        var data = new ResetData { context_clues = "" };
        string jsonData = JsonUtility.ToJson(data);
        
        using (UnityWebRequest request = new UnityWebRequest(serverURL + "/reset", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                var response = JsonUtility.FromJson<ResetResponse>(request.downloadHandler.text);
                statusText.text = $"✅ Ready for visitor #{response.total_visitors}";
                
                if (!string.IsNullOrEmpty(response.introduction))
                {
                    responseText.text = $"Bot: {response.introduction}";
                }
            }
            else
            {
                statusText.text = $"❌ Reset failed: {request.error}";
            }
        }
    }
    
    public void SendTestMessage()
    {
        if (chatInputField == null || string.IsNullOrEmpty(chatInputField.text))
            return;
        
        StartCoroutine(SendChatRequest(chatInputField.text));
        chatInputField.text = "";
    }
    
    IEnumerator SendChatRequest(string message)
    {
        var chatData = new ChatMessage { message = message };
        string jsonData = JsonUtility.ToJson(chatData);
        
        using (UnityWebRequest request = new UnityWebRequest(serverURL + "/chat", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                var response = JsonUtility.FromJson<ChatResponse>(request.downloadHandler.text);
                responseText.text = $"Bot: {response.response}";
                Debug.Log($"Exchange #{response.exchange_count}");
            }
            else
            {
                responseText.text = $"❌ Chat failed: {request.error}";
            }
        }
    }
    
    // Update personality/tone/scene mid-conversation
    public void UpdateSettings()
    {
        string personality = personalityDropdown.options[personalityDropdown.value].text;
        string tone = toneDropdown.options[toneDropdown.value].text;
        string scene = sceneDropdown.options[sceneDropdown.value].text;
        
        StartCoroutine(UpdateSettingsRequest(personality, tone, scene));
    }
    
    IEnumerator UpdateSettingsRequest(string personality, string tone, string scene)
    {
        var settings = new PersonalitySettings
        {
            personality = personality,
            tone = tone,
            scene = scene
        };
        
        string jsonData = JsonUtility.ToJson(settings);
        
        using (UnityWebRequest request = new UnityWebRequest(serverURL + "/set_personality", "POST"))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonData);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();
            
            if (request.result == UnityWebRequest.Result.Success)
            {
                statusText.text = "✅ Settings updated mid-conversation";
            }
        }
    }
}

// Data classes for JSON serialization
[Serializable]
public class HealthResponse
{
    public string status;
    public bool bot_initialized;
    public bool reachy_connected;
}

[Serializable]
public class AvailableOptions
{
    public string[] personalities;
    public string[] tones;
    public string[] scenes;
}

[Serializable]
public class InitializeConfig
{
    public string personality;
    public string tone;
    public string scene;
    public string custom_scene;
}

[Serializable]
public class StandardResponse
{
    public string status;
    public string message;
}

[Serializable]
public class ResetData
{
    public string context_clues;
}

[Serializable]
public class ResetResponse
{
    public string status;
    public string message;
    public int total_visitors;
    public string introduction;
}

[Serializable]
public class ChatMessage
{
    public string message;
}

[Serializable]
public class ChatResponse
{
    public string status;
    public string response;
    public int exchange_count;
}

[Serializable]
public class PersonalitySettings
{
    public string personality;
    public string tone;
    public string scene;
}