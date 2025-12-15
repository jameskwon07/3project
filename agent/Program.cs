using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace Agent;

/// <summary>
/// Agent - Client that connects to Master server and reports status
/// </summary>
class Program
{
    private static readonly HttpClient httpClient = new HttpClient();
    private static string masterUrl = "http://localhost:8000";
    private static string agentName = Environment.MachineName;
    private static string agentPlatform = GetPlatform();
    private static string agentVersion = "1.0.0";
    private static string agentId = "";
    private static bool running = true;

    static async Task Main(string[] args)
    {
        Console.WriteLine($"🚀 Agent started");
        Console.WriteLine($"   Name: {agentName}");
        Console.WriteLine($"   Platform: {agentPlatform}");
        Console.WriteLine($"   Version: {agentVersion}");
        Console.WriteLine($"   Master URL: {masterUrl}");

        // Parse command line arguments
        if (args.Length > 0)
        {
            masterUrl = args[0];
        }

        // Handle Ctrl+C
        Console.CancelKeyPress += (sender, e) =>
        {
            e.Cancel = true;
            running = false;
            Console.WriteLine("\n⏹️  Shutting down...");
        };

        // Register with Master
        await RegisterToMaster();

        // Send heartbeat and check for deployments periodically (every 10 seconds)
        var heartbeatTask = Task.Run(async () =>
        {
            while (running)
            {
                await Task.Delay(10000);
                if (running)
                {
                    await SendHeartbeat();
                    await CheckForDeployment();
                }
            }
        });

        // Main loop
        Console.WriteLine("✓ Connected to Master. Sending heartbeat...");
        Console.WriteLine("  (Press Ctrl+C to exit)");

        await heartbeatTask;
        
        // Unregister on exit
        await UnregisterFromMaster();
        Console.WriteLine("✅ Agent stopped");
    }

    static async Task RegisterToMaster()
    {
        try
        {
            var request = new
            {
                name = agentName,
                platform = agentPlatform,
                version = agentVersion,
                ip_address = GetLocalIPAddress()
            };

            var response = await httpClient.PostAsJsonAsync(
                $"{masterUrl}/api/agents/register",
                request
            );

            if (response.IsSuccessStatusCode)
            {
                var agent = await response.Content.ReadFromJsonAsync<AgentResponse>();
                agentId = agent?.id ?? "";
                Console.WriteLine($"✓ Registered with Master (ID: {agentId})");
            }
            else
            {
                Console.WriteLine($"⚠️  Registration failed: {response.StatusCode}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Failed to connect to Master: {ex.Message}");
            Console.WriteLine("   Please check if Master server is running.");
        }
    }

    static async Task SendHeartbeat()
    {
        try
        {
            var request = new
            {
                name = agentName,
                platform = agentPlatform,
                version = agentVersion,
                ip_address = GetLocalIPAddress()
            };

            await httpClient.PostAsJsonAsync(
                $"{masterUrl}/api/agents/register",
                request
            );
        }
        catch (Exception ex)
        {
            Console.WriteLine($"⚠️  Heartbeat failed: {ex.Message}");
        }
    }

    static async Task UnregisterFromMaster()
    {
        try
        {
            if (!string.IsNullOrEmpty(agentId))
            {
                await httpClient.DeleteAsync($"{masterUrl}/api/agents/{agentId}");
                Console.WriteLine("✓ Unregistered from Master");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"⚠️  Unregistration failed: {ex.Message}");
        }
    }

    static async Task CheckForDeployment()
    {
        if (string.IsNullOrEmpty(agentId))
        {
            return;
        }

        try
        {
            var response = await httpClient.GetAsync($"{masterUrl}/api/deployments/pending/{agentId}");
            
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                
                // Check if response is null or empty (no pending deployment)
                if (string.IsNullOrWhiteSpace(content) || content == "null")
                {
                    return;
                }

                var deployment = JsonConvert.DeserializeObject<DeploymentResponse>(content);
                
                if (deployment != null && !string.IsNullOrEmpty(deployment.id))
                {
                    Console.WriteLine($"📦 Received deployment: {deployment.id}");
                    Console.WriteLine($"   Releases: {string.Join(", ", deployment.release_tags ?? new List<string>())}");
                    await ExecuteDeployment(deployment);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"⚠️  Failed to check for deployment: {ex.Message}");
        }
    }

    static async Task ExecuteDeployment(DeploymentResponse deployment)
    {
        try
        {
            Console.WriteLine($"🚀 Executing deployment: {deployment.id}...");
            
            // TODO: Implement actual deployment logic here
            // For now, simulate deployment with a delay
            await Task.Delay(2000); // Simulate deployment time
            
            // Simulate success (in real implementation, check actual deployment result)
            bool success = true;
            string errorMessage = null;
            
            // TODO: Replace with actual deployment logic:
            // 1. Download release artifacts from GitHub
            // 2. Install/update software on the target system
            // 3. Verify installation
            // 4. Set success/failure based on result
            
            if (success)
            {
                Console.WriteLine($"✅ Deployment {deployment.id} completed successfully");
                await ReportDeploymentComplete(deployment.id, "success", null);
            }
            else
            {
                Console.WriteLine($"❌ Deployment {deployment.id} failed: {errorMessage ?? "Unknown error"}");
                await ReportDeploymentComplete(deployment.id, "failed", errorMessage);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Deployment execution failed: {ex.Message}");
            await ReportDeploymentComplete(deployment.id, "failed", ex.Message);
        }
    }

    static async Task ReportDeploymentComplete(string deploymentId, string status, string errorMessage)
    {
        try
        {
            var request = new
            {
                status = status,
                error_message = errorMessage
            };

            var response = await httpClient.PostAsJsonAsync(
                $"{masterUrl}/api/deployments/{deploymentId}/complete",
                request
            );

            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine($"✓ Deployment status reported: {status}");
            }
            else
            {
                Console.WriteLine($"⚠️  Failed to report deployment status: {response.StatusCode}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"⚠️  Failed to report deployment completion: {ex.Message}");
        }
    }

    static string GetPlatform()
    {
        var platform = Environment.OSVersion.Platform;
        if (platform == PlatformID.Win32NT)
            return "windows";
        else if (platform == PlatformID.MacOSX || platform == PlatformID.Unix)
            return "macos";
        else
            return "unknown";
    }

    static string GetLocalIPAddress()
    {
        try
        {
            var host = System.Net.Dns.GetHostEntry(System.Net.Dns.GetHostName());
            foreach (var ip in host.AddressList)
            {
                if (ip.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)
                {
                    return ip.ToString();
                }
            }
        }
        catch { }
        return null;
    }

    class AgentResponse
    {
        public string id { get; set; }
        public string name { get; set; }
        public string platform { get; set; }
        public string version { get; set; }
        public string status { get; set; }
    }

    class DeploymentResponse
    {
        public string id { get; set; }
        public string agent_id { get; set; }
        public string agent_name { get; set; }
        public List<string> release_ids { get; set; }
        public List<string> release_tags { get; set; }
        public string status { get; set; }
        public DateTime created_at { get; set; }
        public DateTime? started_at { get; set; }
        public DateTime? completed_at { get; set; }
        public string error_message { get; set; }
    }
}
