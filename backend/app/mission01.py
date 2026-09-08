"""Authoritative Mission 01 seed content. Never import this module in the frontend."""

TITLE = "Reconnaissance Fundamentals"
DESCRIPTION = """Web Server Attack Surface Reconnaissance

You are conducting an authorized internal security assessment for Northbridge Systems. Investigate its newly deployed status portal and map the exposed attack surface before vulnerability analysis. This mission is reconnaissance only; exploitation and authentication attacks are outside scope.

All activity takes place inside the isolated OffSec Lab environment. Start the lab, then use the provided attacker environment to investigate only target-m01. Never run these investigations against Internet or other external systems.

Learning objectives: explain Host Discovery and distinguish it from Port Scanning; identify open TCP ports with Nmap; understand why a port number alone does not prove a service; enumerate services and versions; inspect HTTP with curl; explain how these observations support an authorized vulnerability assessment before any vulnerability analysis or exploitation.

Follow Host Discovery → Port Scan → Service Enumeration → Version Detection → HTTP Inspection. Each challenge provides three progressive hints: reasoning, technique, then a command example. Interpret the output yourself and record your findings."""

LEARNING_EXPLANATION = """Reconnaissance
Reconnaissance collects information about a target before vulnerability analysis or exploitation. Its purpose is to understand the attack surface before attempting an attack.

Host Discovery
Host Discovery asks, “Can I reach this target?” Echo replies provide reachability evidence. A missing reply may indicate filtering or a network-path problem, rather than proving a host is offline. Investigate reachability before deeper enumeration.

Port Scanning
Port scanning identifies network endpoints that accept connections. These open ports form part of the observable attack surface. Discovery tests reachability; scanning identifies listening endpoints. An open port is not itself a vulnerability.

Service Enumeration
A port number is only a convention. Probe the endpoint to identify the actual protocol or application; do not assume its identity solely from the port number.

Version Detection
Product and version evidence helps identify deployed software and potentially relevant security advisories. A detected version alone does not prove a vulnerability: distribution patches and configuration also matter. Distinguish the upstream version from package revisions and custom banner suffixes.

HTTP Inspection
After identifying HTTP, move to application-layer reconnaissance: inspect status codes, response headers, server metadata, the page title, and application behavior. Exposed paths and resources can inform later investigation. This mission covers only basic HTTP inspection; directory enumeration and web vulnerability testing belong to later missions.

Real-World Vulnerability Assessment
The authorized workflow is Target Scope → Reachability → Port Discovery → Service Enumeration → Version Identification → Application Enumeration → Vulnerability Analysis. Mission 01 practices its early reconnaissance and enumeration phases. Nmap and curl support an investigation; memorizing tool names is not the objective. Explain what each observation establishes, its limitations, and why you would collect it before assessing vulnerabilities."""

# title, public task, backend-only answer, hints in level order
CHALLENGES = [
    (
        "Host Discovery",
        "Confirm that target-m01 responds to network reachability checks from the attacker environment before deeper enumeration. After receiving replies, submit the lowercase English word meaning 'can be reached' (9 letters).",
        "reachable",
        [
            "Before scanning services, determine whether the target host can be reached from your current environment.",
            "A common first check sends an ICMP Echo Request and looks for an Echo Reply.",
            "From the attacker environment, run: ping -c 4 target-m01\nInterpret the replies, then submit the reachability word described in the task.",
        ],
    ),
    (
        "Port Scan",
        "Identify all open TCP ports on target-m01. These listening endpoints form part of its network attack surface. Submit the ports in ascending order as port,port, without spaces.",
        "22,80",
        [
            "A host that responds may expose network services. Determine which TCP ports accept connections.",
            "Nmap reports open TCP ports. Check the complete TCP port range instead of assuming only common ports matter.",
            "From the attacker environment, run: nmap -p- target-m01\nFind the ports reported as open and submit them in ascending order.",
        ],
    ),
    (
        "Service Enumeration",
        "Determine the services on target-m01 ports 22/tcp and 80/tcp. A port number alone does not prove a service's identity. Submit service,service, without spaces, in port order 22 then 80.",
        "ssh,http",
        [
            "Port numbers alone do not guarantee which applications are running. Identify the services behind the open ports.",
            "Nmap Service Detection probes open ports to identify the application protocol or service.",
            "From the attacker environment, run: nmap -sV -p 22,80 target-m01\nInterpret the SERVICE column in the requested port order.",
        ],
    ),
    (
        "Version Detection",
        "Determine the SSH product and upstream version detected on target-m01 port 22/tcp. Submit product and version only, separated by a space. Exclude the Debian package revision and OffSec Lab banner suffix. This evidence supports later vulnerability analysis.",
        "OpenSSH 9.2p1",
        [
            "After identifying a service, ask which software implementation and version is running. Compare this evidence with security advisories during later analysis.",
            "Nmap service/version detection provides more detail than a normal port scan. Focus on the version information for port 22.",
            "From the attacker environment, run: nmap -sV -p 22 target-m01\nRead VERSION and extract only the SSH product and upstream version.",
        ],
    ),
    (
        "HTTP Inspection",
        "Inspect target-m01's HTTP service on port 80. Observe the HTTP status, response headers, Server header if present, and HTML document title. Submit only the text inside the HTML title element. This moves investigation from the network layer to application metadata.",
        "Northbridge Systems Status Portal",
        [
            "An HTTP service allows application-level inspection. Examine what the web server actually returns.",
            "curl displays response headers and HTML without a browser. The HTML title element contains useful application metadata.",
            "From the attacker environment, run: curl -i http://target-m01\nThen inspect the title with: curl -s http://target-m01 | grep -i '<title>'\nSubmit the text inside the title element.",
        ],
    ),
]
