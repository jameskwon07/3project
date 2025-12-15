using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using Moq;
using Moq.Protected;
using Newtonsoft.Json;
using Xunit;

namespace Agent.Tests;

/// <summary>
/// Unit tests for Agent deployment execution functionality
/// Uses mocks for external system integration (Master API, GitHub, file system)
/// </summary>
public class DeploymentExecutionTests
{
    private readonly Mock<HttpMessageHandler> _httpMessageHandlerMock;
    private readonly HttpClient _httpClient;
    
    public DeploymentExecutionTests()
    {
        _httpMessageHandlerMock = new Mock<HttpMessageHandler>();
        _httpClient = new HttpClient(_httpMessageHandlerMock.Object);
    }
    
    [Fact]
    public void DeploymentResponse_Deserialization_ShouldWork()
    {
        // Arrange
        var json = @"{
            ""id"": ""deploy-123"",
            ""agent_id"": ""agent-456"",
            ""agent_name"": ""TestAgent"",
            ""release_ids"": [""release-1"", ""release-2""],
            ""release_tags"": [""v1.0.0"", ""v1.1.0""],
            ""status"": ""pending"",
            ""created_at"": ""2024-01-15T10:00:00Z"",
            ""started_at"": null,
            ""completed_at"": null,
            ""error_message"": null
        }";
        
        // Act
        var deployment = JsonConvert.DeserializeObject<DeploymentResponse>(json);
        
        // Assert
        Assert.NotNull(deployment);
        Assert.Equal("deploy-123", deployment.id);
        Assert.Equal("agent-456", deployment.agent_id);
        Assert.Equal(2, deployment.release_ids.Count);
        Assert.Equal("v1.0.0", deployment.release_tags[0]);
    }
    
    [Fact]
    public void ReleaseResponse_Deserialization_ShouldWork()
    {
        // Arrange
        var json = @"{
            ""id"": ""release-1"",
            ""tag_name"": ""v1.0.0"",
            ""name"": ""Test Release"",
            ""version"": ""1.0.0"",
            ""release_date"": ""2024-01-15T10:00:00Z"",
            ""download_url"": ""https://github.com/owner/repo/releases/"",
            ""description"": ""Test description"",
            ""assets"": [""app.exe"", ""app.dmg""]
        }";
        
        // Act
        var release = JsonConvert.DeserializeObject<ReleaseResponse>(json);
        
        // Assert
        Assert.NotNull(release);
        Assert.Equal("release-1", release.id);
        Assert.Equal("v1.0.0", release.tag_name);
        Assert.Equal("https://github.com/owner/repo/releases/", release.download_url);
        Assert.Equal(2, release.assets.Count);
    }
    
    [Fact]
    public async Task FetchReleaseDetails_ShouldReturnRelease_WhenApiCallSucceeds()
    {
        // Arrange
        var releaseJson = @"{
            ""id"": ""release-1"",
            ""tag_name"": ""v1.0.0"",
            ""name"": ""Test Release"",
            ""version"": ""1.0.0"",
            ""release_date"": ""2024-01-15T10:00:00Z"",
            ""download_url"": ""https://github.com/owner/repo/releases/"",
            ""description"": ""Test"",
            ""assets"": []
        }";
        
        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.Is<HttpRequestMessage>(req => 
                    req.Method == HttpMethod.Get && 
                    req.RequestUri.ToString().Contains("/api/releases/release-1")),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = System.Net.HttpStatusCode.OK,
                Content = new StringContent(releaseJson)
            });
        
        // Act
        var release = await FetchReleaseDetails("release-1", _httpClient, "http://localhost:8000");
        
        // Assert
        Assert.NotNull(release);
        Assert.Equal("release-1", release.id);
        Assert.Equal("v1.0.0", release.tag_name);
    }
    
    [Fact]
    public async Task FetchReleaseDetails_ShouldReturnNull_WhenApiCallFails()
    {
        // Arrange
        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = System.Net.HttpStatusCode.NotFound
            });
        
        // Act
        var release = await FetchReleaseDetails("nonexistent", _httpClient, "http://localhost:8000");
        
        // Assert
        Assert.Null(release);
    }
    
    [Fact]
    public void ExtractGitHubOwnerAndRepo_ShouldExtractCorrectly()
    {
        // Arrange
        var githubUrl = "https://github.com/jameskwon07/3project/releases/";
        var pattern = @"https://github\.com/([^/]+)/([^/]+)";
        
        // Act
        var match = System.Text.RegularExpressions.Regex.Match(githubUrl.TrimEnd('/'), pattern);
        
        // Assert
        Assert.True(match.Success);
        Assert.Equal("jameskwon07", match.Groups[1].Value);
        Assert.Equal("3project", match.Groups[2].Value);
    }
    
    [Fact]
    public void ExtractGitHubOwnerAndRepo_ShouldFail_WhenUrlIsInvalid()
    {
        // Arrange
        var invalidUrl = "https://invalid-url.com/repo";
        var pattern = @"https://github\.com/([^/]+)/([^/]+)";
        
        // Act
        var match = System.Text.RegularExpressions.Regex.Match(invalidUrl, pattern);
        
        // Assert
        Assert.False(match.Success);
    }
    
    [Fact]
    public void VerifyInstallation_ShouldReturnTrue_WhenFileExists()
    {
        // Arrange
        var tempFile = Path.GetTempFileName();
        try
        {
            File.WriteAllText(tempFile, "test content");
            
            // Act
            var result = VerifyInstallation(tempFile, "windows");
            
            // Assert
            Assert.True(result);
        }
        finally
        {
            File.Delete(tempFile);
        }
    }
    
    [Fact]
    public void VerifyInstallation_ShouldReturnFalse_WhenFileDoesNotExist()
    {
        // Arrange
        var nonexistentFile = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
        
        // Act
        var result = VerifyInstallation(nonexistentFile, "windows");
        
        // Assert
        Assert.False(result);
    }
    
    [Fact]
    public void VerifyInstallation_ShouldReturnFalse_WhenFileIsEmpty()
    {
        // Arrange
        var emptyFile = Path.GetTempFileName();
        try
        {
            // File is already empty
            
            // Act
            var result = VerifyInstallation(emptyFile, "windows");
            
            // Assert
            Assert.False(result);
        }
        finally
        {
            File.Delete(emptyFile);
        }
    }
    
    // Helper methods that mirror the implementation (for testing)
    private static async Task<ReleaseResponse?> FetchReleaseDetails(string releaseId, HttpClient httpClient, string masterUrl)
    {
        try
        {
            var response = await httpClient.GetAsync($"{masterUrl}/api/releases/{releaseId}");
            
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<ReleaseResponse>(content);
            }
            else
            {
                return null;
            }
        }
        catch
        {
            return null;
        }
    }
    
    private static bool VerifyInstallation(string filePath, string platform)
    {
        try
        {
            if (!File.Exists(filePath))
            {
                return false;
            }
            
            var fileInfo = new FileInfo(filePath);
            if (fileInfo.Length == 0)
            {
                return false;
            }
            
            if (platform == "macos" || platform == "linux")
            {
                return true; // Simplified check
            }
            else if (platform == "windows")
            {
                return filePath.EndsWith(".exe", StringComparison.OrdinalIgnoreCase);
            }
            
            return true;
        }
        catch
        {
            return false;
        }
    }
    
    // Test data classes
    private class DeploymentResponse
    {
        public string id { get; set; } = "";
        public string agent_id { get; set; } = "";
        public string agent_name { get; set; } = "";
        public List<string> release_ids { get; set; } = new();
        public List<string> release_tags { get; set; } = new();
        public string status { get; set; } = "";
        public DateTime created_at { get; set; }
        public DateTime? started_at { get; set; }
        public DateTime? completed_at { get; set; }
        public string? error_message { get; set; }
    }
    
    private class ReleaseResponse
    {
        public string id { get; set; } = "";
        public string tag_name { get; set; } = "";
        public string name { get; set; } = "";
        public string version { get; set; } = "";
        public DateTime release_date { get; set; }
        public string download_url { get; set; } = "";
        public string description { get; set; } = "";
        public List<string> assets { get; set; } = new();
    }
}

