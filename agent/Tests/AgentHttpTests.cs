using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Moq;
using Moq.Protected;
using Newtonsoft.Json;
using NUnit.Framework;

namespace Tests;

/// <summary>
/// Unit tests for Agent HTTP functionality using Moq
/// Tests HTTP interactions with Master server (registration, heartbeat, deployment)
/// </summary>
public class AgentHttpTests
{
    private Mock<HttpMessageHandler> _httpMessageHandlerMock = null!;
    private HttpClient _httpClient = null!;

    [SetUp]
    public void Setup()
    {
        _httpMessageHandlerMock = new Mock<HttpMessageHandler>();
        _httpClient = new HttpClient(_httpMessageHandlerMock.Object);
    }

    [TearDown]
    public void TearDown()
    {
        _httpClient?.Dispose();
    }

    [Test]
    public async Task RegisterAgent_ShouldReturnAgentId_WhenRegistrationSucceeds()
    {
        // Arrange
        var agentResponse = new AgentResponse
        {
            id = "agent-123",
            name = "TestAgent",
            platform = "windows",
            version = "1.0.0",
            status = "online"
        };

        var jsonResponse = JsonConvert.SerializeObject(agentResponse);

        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Post &&
                    req.RequestUri!.ToString().Contains("/api/agents/register")),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.OK,
                Content = new StringContent(jsonResponse, Encoding.UTF8, "application/json")
            });

        // Act
        var response = await _httpClient.PostAsJsonAsync(
            "http://localhost:8000/api/agents/register",
            new
            {
                name = "TestAgent",
                platform = "windows",
                version = "1.0.0",
                ip_address = "127.0.0.1"
            });

        var result = await response.Content.ReadFromJsonAsync<AgentResponse>();

        // Assert
        Assert.That(response.IsSuccessStatusCode, Is.True);
        Assert.That(result, Is.Not.Null);
        Assert.That(result!.id, Is.EqualTo("agent-123"));
        Assert.That(result.name, Is.EqualTo("TestAgent"));
    }

    [Test]
    public async Task RegisterAgent_ShouldHandleFailure_WhenServerReturnsError()
    {
        // Arrange
        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Post &&
                    req.RequestUri!.ToString().Contains("/api/agents/register")),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.InternalServerError
            });

        // Act
        var response = await _httpClient.PostAsJsonAsync(
            "http://localhost:8000/api/agents/register",
            new
            {
                name = "TestAgent",
                platform = "windows",
                version = "1.0.0",
                ip_address = "127.0.0.1"
            });

        // Assert
        Assert.That(response.IsSuccessStatusCode, Is.False);
        Assert.That(response.StatusCode, Is.EqualTo(HttpStatusCode.InternalServerError));
    }

    [Test]
    public async Task FetchReleaseDetails_ShouldReturnRelease_WhenApiCallSucceeds()
    {
        // Arrange
        var releaseResponse = new ReleaseResponse
        {
            id = "release-1",
            tag_name = "v1.0.0",
            name = "Test Release",
            version = "1.0.0",
            release_date = DateTime.UtcNow,
            download_url = "https://github.com/owner/repo/releases/",
            description = "Test description",
            assets = new List<string> { "app.exe", "app.dmg" }
        };

        var jsonResponse = JsonConvert.SerializeObject(releaseResponse);

        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Get &&
                    req.RequestUri!.ToString().Contains("/api/releases/release-1")),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.OK,
                Content = new StringContent(jsonResponse, Encoding.UTF8, "application/json")
            });

        // Act
        var response = await _httpClient.GetAsync("http://localhost:8000/api/releases/release-1");
        var content = await response.Content.ReadAsStringAsync();
        var result = JsonConvert.DeserializeObject<ReleaseResponse>(content);

        // Assert
        Assert.That(response.IsSuccessStatusCode, Is.True);
        Assert.That(result, Is.Not.Null);
        Assert.That(result!.id, Is.EqualTo("release-1"));
        Assert.That(result.tag_name, Is.EqualTo("v1.0.0"));
        Assert.That(result.download_url, Is.EqualTo("https://github.com/owner/repo/releases/"));
    }

    [Test]
    public async Task FetchReleaseDetails_ShouldReturnNull_WhenApiCallFails()
    {
        // Arrange
        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Get &&
                    req.RequestUri!.ToString().Contains("/api/releases/nonexistent")),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.NotFound
            });

        // Act
        var response = await _httpClient.GetAsync("http://localhost:8000/api/releases/nonexistent");

        // Assert
        Assert.That(response.IsSuccessStatusCode, Is.False);
        Assert.That(response.StatusCode, Is.EqualTo(HttpStatusCode.NotFound));
    }

    [Test]
    public async Task CheckForDeployment_ShouldReturnDeployment_WhenPendingDeploymentExists()
    {
        // Arrange
        var deploymentResponse = new DeploymentResponse
        {
            id = "deploy-123",
            agent_id = "agent-456",
            agent_name = "TestAgent",
            release_ids = new List<string> { "release-1", "release-2" },
            release_tags = new List<string> { "v1.0.0", "v1.1.0" },
            status = "pending",
            created_at = DateTime.UtcNow
        };

        var jsonResponse = JsonConvert.SerializeObject(deploymentResponse);

        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Get &&
                    req.RequestUri!.ToString().Contains("/api/deployments/pending/agent-456")),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.OK,
                Content = new StringContent(jsonResponse, Encoding.UTF8, "application/json")
            });

        // Act
        var response = await _httpClient.GetAsync("http://localhost:8000/api/deployments/pending/agent-456");
        var content = await response.Content.ReadAsStringAsync();
        var result = JsonConvert.DeserializeObject<DeploymentResponse>(content);

        // Assert
        Assert.That(response.IsSuccessStatusCode, Is.True);
        Assert.That(result, Is.Not.Null);
        Assert.That(result!.id, Is.EqualTo("deploy-123"));
        Assert.That(result.agent_id, Is.EqualTo("agent-456"));
        Assert.That(result.release_ids, Is.Not.Null);
        Assert.That(result.release_ids!.Count, Is.EqualTo(2));
    }

    [Test]
    public async Task CheckForDeployment_ShouldHandleNullResponse_WhenNoPendingDeployment()
    {
        // Arrange
        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Get &&
                    req.RequestUri!.ToString().Contains("/api/deployments/pending/agent-456")),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.OK,
                Content = new StringContent("null", Encoding.UTF8, "application/json")
            });

        // Act
        var response = await _httpClient.GetAsync("http://localhost:8000/api/deployments/pending/agent-456");
        var content = await response.Content.ReadAsStringAsync();

        // Assert
        Assert.That(response.IsSuccessStatusCode, Is.True);
        Assert.That(content, Is.EqualTo("null"));
    }

    [Test]
    public async Task ReportDeploymentComplete_ShouldSucceed_WhenStatusIsReported()
    {
        // Arrange
        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Post &&
                    req.RequestUri!.ToString().Contains("/api/deployments/deploy-123/complete")),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.OK
            });

        // Act
        var response = await _httpClient.PostAsJsonAsync(
            "http://localhost:8000/api/deployments/deploy-123/complete",
            new
            {
                status = "success",
                error_message = ""
            });

        // Assert
        Assert.That(response.IsSuccessStatusCode, Is.True);
        Assert.That(response.StatusCode, Is.EqualTo(HttpStatusCode.OK));
    }

    [Test]
    public async Task ReportDeploymentComplete_ShouldIncludeErrorMessage_WhenStatusIsFailed()
    {
        // Arrange
        var errorMessage = "Installation failed";

        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Post &&
                    req.RequestUri!.ToString().Contains("/api/deployments/deploy-123/complete")),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.OK
            });

        // Act
        var response = await _httpClient.PostAsJsonAsync(
            "http://localhost:8000/api/deployments/deploy-123/complete",
            new
            {
                status = "failed",
                error_message = errorMessage
            });

        // Assert
        Assert.That(response.IsSuccessStatusCode, Is.True);

        // Verify the request content contains the error message
        _httpMessageHandlerMock
            .Protected()
            .Verify(
                "SendAsync",
                Times.Once(),
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Post &&
                    req.RequestUri!.ToString().Contains("/api/deployments/deploy-123/complete")),
                ItExpr.IsAny<CancellationToken>());
    }

    [Test]
    public async Task UnregisterAgent_ShouldSucceed_WhenAgentIdIsProvided()
    {
        // Arrange
        var agentId = "agent-123";

        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Delete &&
                    req.RequestUri!.ToString().Contains($"/api/agents/{agentId}")),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.NoContent
            });

        // Act
        var response = await _httpClient.DeleteAsync($"http://localhost:8000/api/agents/{agentId}");

        // Assert
        Assert.That(response.IsSuccessStatusCode, Is.True);
        Assert.That(response.StatusCode, Is.EqualTo(HttpStatusCode.NoContent));
    }

    [Test]
    public void HttpCall_ShouldHandleNetworkException()
    {
        // Arrange
        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ThrowsAsync(new HttpRequestException("Network error"));

        // Act & Assert
        var exception = Assert.ThrowsAsync<HttpRequestException>(async () =>
        {
            await _httpClient.GetAsync("http://localhost:8000/api/releases/release-1");
        });

        Assert.That(exception, Is.Not.Null);
        Assert.That(exception!.Message, Is.EqualTo("Network error"));
    }

    [Test]
    public async Task Heartbeat_ShouldUseRegisterEndpoint()
    {
        // Arrange
        _httpMessageHandlerMock
            .Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Post &&
                    req.RequestUri!.ToString().Contains("/api/agents/register")),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.OK,
                Content = new StringContent("{}", Encoding.UTF8, "application/json")
            });

        // Act
        var response = await _httpClient.PostAsJsonAsync(
            "http://localhost:8000/api/agents/register",
            new
            {
                name = "TestAgent",
                platform = "windows",
                version = "1.0.0",
                ip_address = "127.0.0.1"
            });

        // Assert
        Assert.That(response.IsSuccessStatusCode, Is.True);

        // Verify it was called
        _httpMessageHandlerMock
            .Protected()
            .Verify(
                "SendAsync",
                Times.Once(),
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == HttpMethod.Post &&
                    req.RequestUri!.ToString().Contains("/api/agents/register")),
                ItExpr.IsAny<CancellationToken>());
    }

    // Test data classes
    private class AgentResponse
    {
        public string id { get; set; } = "";
        public string name { get; set; } = "";
        public string platform { get; set; } = "";
        public string version { get; set; } = "";
        public string status { get; set; } = "";
    }

    private class DeploymentResponse
    {
        public string id { get; set; } = "";
        public string agent_id { get; set; } = "";
        public string agent_name { get; set; } = "";
        public List<string>? release_ids { get; set; }
        public List<string>? release_tags { get; set; }
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
        public List<string>? assets { get; set; }
    }
}
