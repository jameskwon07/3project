using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace Agent;

/// <summary>
/// Agent - Master 서버에 연결하여 상태를 보고하는 클라이언트
/// </summary>
class Program
{
    private static readonly HttpClient httpClient = new HttpClient();
    private static string masterUrl = "http://localhost:8000";
    private static string agentName = Environment.MachineName;
    private static string agentPlatform = GetPlatform();
    private static string agentVersion = "1.0.0";
    private static bool running = true;

    static async Task Main(string[] args)
    {
        Console.WriteLine($"🚀 Agent 시작");
        Console.WriteLine($"   이름: {agentName}");
        Console.WriteLine($"   플랫폼: {agentPlatform}");
        Console.WriteLine($"   버전: {agentVersion}");
        Console.WriteLine($"   Master URL: {masterUrl}");

        // 명령줄 인자 파싱
        if (args.Length > 0)
        {
            masterUrl = args[0];
        }

        // Ctrl+C 핸들링
        Console.CancelKeyPress += (sender, e) =>
        {
            e.Cancel = true;
            running = false;
            Console.WriteLine("\n⏹️  종료 중...");
        };

        // Master에 등록
        await RegisterToMaster();

        // 주기적으로 하트비트 전송 (10초마다)
        var heartbeatTask = Task.Run(async () =>
        {
            while (running)
            {
                await Task.Delay(10000);
                if (running)
                {
                    await SendHeartbeat();
                }
            }
        });

        // 메인 루프
        Console.WriteLine("✓ Master에 연결됨. 하트비트 전송 중...");
        Console.WriteLine("  (Ctrl+C로 종료)");

        await heartbeatTask;
        
        // 종료 시 등록 해제
        await UnregisterFromMaster();
        Console.WriteLine("✅ Agent 종료됨");
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
                Console.WriteLine($"✓ Master에 등록됨 (ID: {agent?.id})");
            }
            else
            {
                Console.WriteLine($"⚠️  등록 실패: {response.StatusCode}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Master 연결 실패: {ex.Message}");
            Console.WriteLine("   Master 서버가 실행 중인지 확인하세요.");
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
            Console.WriteLine($"⚠️  하트비트 전송 실패: {ex.Message}");
        }
    }

    static async Task UnregisterFromMaster()
    {
        try
        {
            var agentId = $"{agentPlatform}-{agentName}";
            await httpClient.DeleteAsync($"{masterUrl}/api/agents/{agentId}");
            Console.WriteLine("✓ Master에서 등록 해제됨");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"⚠️  등록 해제 실패: {ex.Message}");
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
}

