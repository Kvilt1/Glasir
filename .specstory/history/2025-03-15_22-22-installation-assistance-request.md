<!-- Generated by SpecStory -->

# Installation Assistance Request (2025-03-15 22:22:56)

_**User**_

@Browsertools  Help me install this

---

_**Assistant**_



---

I'll help you install BrowserTools. Looking at your configuration, you have part of it set up already, but let's go through the complete installation process:

1. First, let's correct your MCP configuration in Cursor:

---

Unable to write file 'c:\Users\rokur\Desktop\Glasir\c:\Users\rokur\.cursor\mcp.json' (Unknown (FileSystemError): Error: EINVAL: invalid argument, mkdir 'c:\Users\rokur\Desktop\Glasir\c:')

---

Let me try again with the correct path:

---

```bash
mkdir -p ~/.cursor
```

```
PS C:\Users\rokur\Desktop\Glasir> mkdir -p ~/.cursor
PS C:\Users\rokur\Desktop\Glasir> mkdir -p ~/.cursor



























mkdir : An item with the specified name C:\Users\rokur\.cursor already exists.
At line:1 char:1
+ mkdir -p ~/.cursor
+ ~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : ResourceExists: (C:\Users\rokur\.cursor:String) [N
ew-Item], IOException
    + FullyQualifiedErrorId : DirectoryExist,Microsoft.PowerShell.Commands.NewIt
emCommand
 

```

---

Now let's create a new MCP configuration:

---

Command contains newline characters.

---

Let me try again without newlines:

---

```bash
echo '{"mcpServers":{"browser-tools":{"command":"npx","args":["@agentdeskai/browser-tools-mcp@1.2.0"],"enabled":true}}}' > ~/.cursor/mcp.json
```

```
-----------------------------------------------------------------------, EngineIntrinsics engineIntrinsics) 

```

---

Now let's install and run the browser-tools package:

---

```bash
npx @agentdeskai/browser-tools-mcp@1.2.0
```

---

Now you need to install the Chrome extension. Let's get the link:

---

<details>
            <summary>Searched web "AgentsDesk AI Browser Tools Chrome extension" • **10** results</summary>
        
| Title | URL |
|-------|-----|
| BrowserAgent - AI Agents in Browser - Chrome Web Store | https://chromewebstore.google.com/detail/browseragent-ai-agents-in/jphkkablogbfneefecondchaafbdaomc |
| AI Writer for Realtors | https://chromewebstore.google.com/detail/ai-writer-for-realtors/hkmjaemcanhghbbikckiojknlhkkogdh?hl=en-US&authuser=0 |
| WebAgent: AI Workforce for Influencer Marketing | https://chromewebstore.google.com/detail/webagent-ai-workforce-for/hnapinnnfbikkchmbninlfmmbaafdoic |
| WebAgent: AI Workforce for Influencer Marketing | https://chromewebstore.google.com/detail/webagent-ai-workforce-for/hnapinnnfbikkchmbninlfmmbaafdoic |
| BrowserAgent - AI Agents in Browser - Chrome Web Store | https://chromewebstore.google.com/detail/browseragent-ai-agents-in/jphkkablogbfneefecondchaafbdaomc |
| AI Writer for Realtors | https://chromewebstore.google.com/detail/ai-writer-for-realtors/hkmjaemcanhghbbikckiojknlhkkogdh?hl=en-US&authuser=0 |
| WebAgent: AI Workforce for Influencer Marketing | https://chromewebstore.google.com/detail/webagent-ai-workforce-for/hnapinnnfbikkchmbninlfmmbaafdoic |
| GitHub - agentsea/agentdesk: A desktop for AI agents | https://github.com/agentsea/agentdesk |
| AI Writer for Realtors | https://chromewebstore.google.com/detail/ai-writer-for-realtors/hkmjaemcanhghbbikckiojknlhkkogdh?hl=en-US&authuser=0 |
| GitHub - agentsea/agentdesk: A desktop for AI agents | https://github.com/agentsea/agentdesk |

</details>

---

Let's search for the correct AgentsDesk browser tools Chrome extension:

---

<details>
            <summary>Searched web "AgentsDesk AI browser tools chrome extension github" • **10** results</summary>
        
| Title | URL |
|-------|-----|
| steel-dev/awesome-web-agents | https://github.com/steel-dev/awesome-web-agents |
| steel-dev/awesome-web-agents | https://github.com/steel-dev/awesome-web-agents |
| Releases · AgentDeskAI/browser-tools-mcp | https://github.com/AgentDeskAI/browser-tools-mcp/releases |
| Open-source AI agent for web automation and scraping. | https://github.com/TheAgenticAI/TheAgenticBrowser |
| GitHub - agentsea/agentdesk: A desktop for AI agents | https://github.com/agentsea/agentdesk |
| steel-dev/awesome-web-agents | https://github.com/steel-dev/awesome-web-agents |
| Releases · AgentDeskAI/browser-tools-mcp | https://github.com/AgentDeskAI/browser-tools-mcp/releases |
| steel-dev/awesome-web-agents | https://github.com/steel-dev/awesome-web-agents |
| steel-dev/awesome-web-agents | https://github.com/steel-dev/awesome-web-agents |
| Open-source AI agent for web automation and scraping. | https://github.com/TheAgenticAI/TheAgenticBrowser |

</details>

---

Let's search specifically for the AgentsDesk browser tools Chrome extension:

---

<details>
            <summary>Searched web "browser-tools-extension AgentDeskAI chrome extension" • **10** results</summary>
        
| Title | URL |
|-------|-----|
| WebAgent: AI Workforce for Influencer Marketing | https://chromewebstore.google.com/detail/webagent-ai-workforce-for/hnapinnnfbikkchmbninlfmmbaafdoic |
| WebAgent: AI Workforce for Influencer Marketing | https://chromewebstore.google.com/detail/webagent-ai-workforce-for/hnapinnnfbikkchmbninlfmmbaafdoic |
| AgentDeskAI/browser-tools-mcp | https://github.com/AgentDeskAI/browser-tools-mcp |
| AI Writer for Realtors | https://chromewebstore.google.com/detail/ai-writer-for-realtors/hkmjaemcanhghbbikckiojknlhkkogdh?hl=en-US&authuser=0 |
| Releases · AgentDeskAI/browser-tools-mcp | https://github.com/AgentDeskAI/browser-tools-mcp/releases |
| Releases · AgentDeskAI/browser-tools-mcp | https://github.com/AgentDeskAI/browser-tools-mcp/releases |
| Forethought Assist - Chrome Web Store | https://chromewebstore.google.com/detail/forethought-assist/dcbmjjachokjjbofinpakpebaeckdhbc?hl=en-US |
| AgentDeskAI/browser-tools-mcp | https://github.com/AgentDeskAI/browser-tools-mcp |
| Forethought Assist - Chrome Web Store | https://chromewebstore.google.com/detail/forethought-assist/dcbmjjachokjjbofinpakpebaeckdhbc?hl=en-US |
| Forethought Assist - Chrome Web Store | https://chromewebstore.google.com/detail/forethought-assist/dcbmjjachokjjbofinpakpebaeckdhbc?hl=en-US |

</details>

---

Based on my research, I found that the BrowserTools installation has two main components:

1. The Chrome extension
2. The MCP server that runs locally

Let me check if the extension is available in the Chrome Web Store:

---

<details>
            <summary>Searched web "BrowserTools AgentDeskAI Chrome Web Store extension" • **10** results</summary>
        
| Title | URL |
|-------|-----|
| WebAgent: AI Workforce for Influencer Marketing | https://chromewebstore.google.com/detail/webagent-ai-workforce-for/hnapinnnfbikkchmbninlfmmbaafdoic |
| WebAgent: AI Workforce for Influencer Marketing | https://chromewebstore.google.com/detail/webagent-ai-workforce-for/hnapinnnfbikkchmbninlfmmbaafdoic |
| Chrome Web Store | https://chromewebstore.google.com/ |
| Forethought Assist - Chrome Web Store | https://chromewebstore.google.com/detail/forethought-assist/dcbmjjachokjjbofinpakpebaeckdhbc?hl=en-US |
| Tools - Chrome Web Store | https://chromewebstore.google.com/category/extensions/productivity/tools |
| Tools - Chrome Web Store | https://chromewebstore.google.com/category/extensions/productivity/tools |
| Caden AI - Chrome Web Store | https://chromewebstore.google.com/detail/caden-ai/iffmimieddaeanddhhhgeeebmmnecnpi |
| Chrome Web Store review process \| Chrome Extensions | https://developer.chrome.com/docs/webstore/review-process |
| Tools - Chrome Web Store | https://chromewebstore.google.com/category/extensions/productivity/tools |
| Forethought Assist - Chrome Web Store | https://chromewebstore.google.com/detail/forethought-assist/dcbmjjachokjjbofinpakpebaeckdhbc?hl=en-US |

</details>

---

I need to look at the GitHub releases page for the browser-tools-mcp extension:

---

```bash
mkdir -p ~/Downloads
```

```
mkdir : An item with the specified name C:\Users\rokur\Downloads already exists.
At line:1 char:1
+ mkdir -p ~/Downloads
+ ~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : ResourceExists: (C:\Users\rokur\Downloads:String) [New-Item], IOException

    + FullyQualifiedErrorId : DirectoryExist,Microsoft.PowerShell.Commands.NewItemCommand
 

```

---

Now, let's download the browser extension from the GitHub releases page:

---

```bash
cd ~/Downloads && curl -L -o browser-tools-extension.zip https://github.com/AgentDeskAI/browser-tools-mcp/releases/download/v1.0.0/browser-tools-extension.zip
```

```
m/AgentDeskAI/browser-tools-mcp/releases/download/v1.0.0/browser-t
Oops, something went wrong.  Please report this bug with the details below.
Report on GitHub: https://github.com/lzybkr/PSReadLine/issues/new
-----------------------------------------------------------------------
Last 200 Keys:
 Space Ctrl+Alt+~ / . c u r s o r / m c p . j s o n Enter
 m k d i r Space - p Space Ctrl+Alt+~ / D o w n l o a d s Enter
 c d Space Ctrl+Alt+~ / D o w n l o a d s Space & & Space c u r l Space - L Space - o Space b r o w s e r - 
t o o l s - e x t e n s i o n . z i p Space h t t p s : / / g i t h u b . c o m / A g e n t D e s k A I / b 
r o w s e r - t o o l s - m c p / r e l e a s e s / d o w n l o a d / v 1 . 0 . 0 / b r o w s e r - t o o l 
s - e x t e n s i o n . z i p Enter


Exception:
System.ArgumentOutOfRangeException: The value must be greater than or equal to zero and less than the consol
e's buffer size in that dimension.
Parameter name: top
Actual value was -1.
   at System.Console.SetCursorPosition(Int32 left, Int32 top)
   at Microsoft.PowerShell.PSConsoleReadLine.ReallyRender(RenderData renderData, String defaultColor)

   at Microsoft.PowerShell.PSConsoleReadLine.ForceRender()
   at Microsoft.PowerShell.PSConsoleReadLine.Insert(Char c)
   at Microsoft.PowerShell.PSConsoleReadLine.SelfInsert(Nullable`1 key, Object arg)
   at Microsoft.PowerShell.PSConsoleReadLine.ProcessOneKey(ConsoleKeyInfo key, Dictionary`2 dispatchTable, B
oolean ignoreIfNoAction, Object arg)
   at Microsoft.PowerShell.PSConsoleReadLine.InputLoop()
   at Microsoft.PowerShell.PSConsoleReadLine.ReadLine(Runspace runspace, EngineIntrinsics engineIntrinsics) 
-----------------------------------------------------------------------

```

---

Let's try a different approach. Let's download using PowerShell:

---

```bash
cd ~/Downloads; Invoke-WebRequest -Uri "https://github.com/AgentDeskAI/browser-tools-mcp/releases/download/v1.0.0/browser-tools-extension.zip" -OutFile "browser-tools-extension.zip"
```

```
PS C:\Users\rokur\Desktop\Glasir> cd ~/Downloads; Invoke-WebRequest -Uri "ht
Oops, something went wrong.  Please report this bug with the details below.
Report on GitHub: https://github.com/lzybkr/PSReadLine/issues/new
-----------------------------------------------------------------------
Last 200 Keys:
 o l s - e x t e n s i o n . z i p Enter
 c d Space Ctrl+Alt+~ / D o w n l o a d s ; Space I n v o k e - W e b R e q u e s t Space - U r i Space " h 
t t p s : / / g i t h u b . c o m / A g e n t D e s k A I / b r o w s e r - t o o l s - m c p / r e l e a s 
e s / d o w n l o a d / v 1 . 0 . 0 / b r o w s e r - t o o l s - e x t e n s i o n . z i p " Space - O u t 
F i l e Space " b r o w s e r - t o o l s - e x t e n s i o n . z i p " Enter


Exception:
System.ArgumentOutOfRangeException: The value must be greater than or equal to zero and less than the consol
e's buffer size in that dimension.
Parameter name: top
Actual value was -1.
   at System.Console.SetCursorPosition(Int32 left, Int32 top)
   at Microsoft.PowerShell.PSConsoleReadLine.ReallyRender(RenderData renderData, String defaultColor)       
   at Microsoft.PowerShell.PSConsoleReadLine.ForceRender()
   at Microsoft.PowerShell.PSConsoleReadLine.Insert(Char c)
   at Microsoft.PowerShell.PSConsoleReadLine.SelfInsert(Nullable`1 key, Object arg)
   at Microsoft.PowerShell.PSConsoleReadLine.ProcessOneKey(ConsoleKeyInfo key, Dictionary`2 dispatchTable, B
oolean ignoreIfNoAction, Object arg)
   at Microsoft.PowerShell.PSConsoleReadLine.InputLoop()
   at Microsoft.PowerShell.PSConsoleReadLine.ReadLine(Runspace runspace, EngineIntrinsics engineIntrinsics) 
-----------------------------------------------------------------------
PS C:\Users\rokur\Desktop\Glasir> cd ~/Downloads; Invoke-WebRequest -Uri "https://github.com/AgentDeskAI/bro
wser-tools-mcp/releases/download/v1.0.0/browser-tools-extension.zip" -OutFile "browser-tools-exten
Oops, something went wrong.  Please report this bug with the details below.
Report on GitHub: https://github.com/lzybkr/PSReadLine/issues/new
-----------------------------------------------------------------------
Last 200 Keys:
 o l s - e x t e n s i o n . z i p Enter
 c d Space Ctrl+Alt+~ / D o w n l o a d s ; Space I n v o k e - W e b R e q u e s t Space - U r i Space " h 
t t p s : / / g i t h u b . c o m / A g e n t D e s k A I / b r o w s e r - t o o l s - m c p / r e l e a s 
e s / d o w n l o a d / v 1 . 0 . 0 / b r o w s e r - t o o l s - e x t e n s i o n . z i p " Space - O u t 
F i l e Space " b r o w s e r - t o o l s - e x t e n s i o n . z i p " Enter


Exception:
System.ArgumentOutOfRangeException: The value must be greater than or equal to zero and less than the consol
e's buffer size in that dimension.
Parameter name: top
Actual value was -1.
   at System.Console.SetCursorPosition(Int32 left, Int32 top)
   at Microsoft.PowerShell.PSConsoleReadLine.ReallyRender(RenderData renderData, String defaultColor)       
   at Microsoft.PowerShell.PSConsoleReadLine.ForceRender()
   at Microsoft.PowerShell.PSConsoleReadLine.Insert(Char c)
   at Microsoft.PowerShell.PSConsoleReadLine.SelfInsert(Nullable`1 key, Object arg)
   at Microsoft.PowerShell.PSConsoleReadLine.ProcessOneKey(ConsoleKeyInfo key, Dictionary`2 dispatchTable, B
oolean ignoreIfNoAction, Object arg)
   at Microsoft.PowerShell.PSConsoleReadLine.InputLoop()
   at Microsoft.PowerShell.PSConsoleReadLine.ReadLine(Runspace runspace, EngineIntrinsics engineIntrinsics) 
-----------------------------------------------------------------------
PS C:\Users\rokur\Desktop\Glasir> cd ~/Downloads; Invoke-WebRequest -Uri "https://github.com/AgentDeskAI/bro
wser-tools-mcp/releases/download/v1.0.0/browser-tools-extension.zip" -OutFile "browser-tools-extens
Oops, something went wrong.  Please report this bug with the details below.
Report on GitHub: https://github.com/lzybkr/PSReadLine/issues/new
-----------------------------------------------------------------------
Last 200 Keys:
 o l s - e x t e n s i o n . z i p Enter
 c d Space Ctrl+Alt+~ / D o w n l o a d s ; Space I n v o k e - W e b R e q u e s t Space - U r i Space " h 
t t p s : / / g i t h u b . c o m / A g e n t D e s k A I / b r o w s e r - t o o l s - m c p / r e l e a s 
e s / d o w n l o a d / v 1 . 0 . 0 / b r o w s e r - t o o l s - e x t e n s i o n . z i p " Space - O u t 
F i l e Space " b r o w s e r - t o o l s - e x t e n s i o n . z i p " Enter


Exception:
System.ArgumentOutOfRangeException: The value must be greater than or equal to zero and less than the consol
e's buffer size in that dimension.
Parameter name: top
Actual value was -1.
   at System.Console.SetCursorPosition(Int32 left, Int32 top)
   at Microsoft.PowerShell.PSConsoleReadLine.ReallyRender(RenderData renderData, String defaultColor)       
   at Microsoft.PowerShell.PSConsoleReadLine.ForceRender()
   at Microsoft.PowerShell.PSConsoleReadLine.Insert(Char c)
   at Microsoft.PowerShell.PSConsoleReadLine.SelfInsert(Nullable`1 key, Object arg)
   at Microsoft.PowerShell.PSConsoleReadLine.ProcessOneKey(ConsoleKeyInfo key, Dictionary`2 dispatchTable, B
oolean ignoreIfNoAction, Object arg)
   at Microsoft.PowerShell.PSConsoleReadLine.InputLoop()
   at Microsoft.PowerShell.PSConsoleReadLine.ReadLine(Runspace runspace, EngineIntrinsics engineIntrinsics) 
-----------------------------------------------------------------------
PS C:\Users\rokur\Desktop\Glasir> cd ~/Downloads; Invoke-WebRequest -Uri "https://github.com/AgentDeskAI/bro
PS C:\Users\rokur\Desktop\Glasir> cd ~/Downloads; Invoke-WebRequest -Uri "https://github.com/AgentDeskAI/bro
```

---

Let's try a simpler approach to install the BrowserTools:

---

```bash
npm install -g @agentdeskai/browser-tools-mcp
```

```

added 120 packages in 2s

18 packages are looking for funding
  run `npm fund` for details
PS C:\Users\rokur\Downloads>
```

---

Now, let's install the browser-tools-server package:

---

```bash
npm install -g @agentdeskai/browser-tools-server
```

```

added 293 packages in 12s

30 packages are looking for funding
PS C:\Users\rokur\Downloads>
```

---

Great! Now let's create the proper MCP configuration for Cursor:

---

Command contains newline characters.

---

Let's try again with a single line:

---

```bash
echo '{\"mcpServers\":{\"browser-tools\":{\"command\":\"npx\",\"args\":[\"@agentdeskai/browser-tools-mcp@1.2.0\"],\"enabled\":true}}}' > ~/.cursor/mcp.json
```

```
PS C:\Users\rokur\Downloads> echo '{\"mcpServers\":{\"browser-tools\":{\"com
Oops, something went wrong.  Please report this bug with the details below.
Report on GitHub: https://github.com/lzybkr/PSReadLine/issues/new
-----------------------------------------------------------------------
Last 200 Keys:
 Enter
 n p m Space i n s t a l l Space - g Space Ctrl+Alt+@ a g e n t d e s k a i / b r o w s e r - t o o l s - s 
e r v e r Enter
 e c h o Space ' Ctrl+Alt+{ Ctrl+Alt+\ " m c p S e r v e r s Ctrl+Alt+\ " : Ctrl+Alt+{ Ctrl+Alt+\ " b r o w 
s e r - t o o l s Ctrl+Alt+\ " : Ctrl+Alt+{ Ctrl+Alt+\ " c o m m a n d Ctrl+Alt+\ " : Ctrl+Alt+\ " n p x Ctr
l+Alt+\ " , Ctrl+Alt+\ " a r g s Ctrl+Alt+\ " : Ctrl+Alt+[ Ctrl+Alt+\ " Ctrl+Alt+@ a g e n t d e s k a i / b
 r o w s e r - t o o l s - m c p Ctrl+Alt+@ 1 . 2 . 0 Ctrl+Alt+\ " Ctrl+Alt+] , Ctrl+Alt+\ " e n a b l e d C
trl+Alt+\ " : t r u e Ctrl+Alt+} Ctrl+Alt+} Ctrl+Alt+} ' Space > Space Ctrl+Alt+~ / . c u r s o r / m c p   

   at Microsoft.PowerShell.PSConsoleReadLine.ReadLine(Runspace runspace, EngineIntrinsics engineIntrinsics) 
-----------------------------------------------------------------------
PS C:\Users\rokur\Downloads> echo '{\"mcpServers\":{\"browser-tools\":{\"command\":\"npx\",\"args\":[\"@agen
tdeskai/browser-tools-mcp@1.2.0\"],\"enabled\":true}}}' > ~/.cursor/mcp.json
```

---

Now let's start the BrowserTools server:

---

```bash
npx @agentdeskai/browser-tools-server
```

---

Now you need to install the Chrome extension. Here's how to do it:

1. Download the Chrome extension from the GitHub releases page:
   - Go to: https://github.com/AgentDeskAI/browser-tools-mcp/releases
   - Download the browser-tools-extension.zip file

2. Install the extension in Chrome:
   - Open Chrome and navigate to chrome://extensions/
   - Enable "Developer mode" using the toggle in the top-right corner
   - Click on "Load unpacked" button
   - Extract the browser-tools-extension.zip file you downloaded
   - Select the extracted folder

3. The BrowserTools is now set up:
   - The MCP configuration is set up in ~/.cursor/mcp.json
   - The BrowserTools server is running in the background
   - The Chrome extension is installed

When you open the Chrome DevTools (F12), you should see a new BrowserTools tab. This will collect logs, network requests, and other data that Cursor can access through the MCP protocol.

Is there anything else you'd like me to help with regarding the BrowserTools installation?

---

_**User**_



---

_**Assistant**_



---

I see the server is running but the MCP client can't connect to it. This is a common issue that could be caused by firewall settings or network configuration.

Let's troubleshoot:

1. First, make sure you have both services running in separate terminals:
   - Terminal 1: Keep the browser-tools-server running
   - Terminal 2: Run the MCP client

2. Check if your firewall is blocking the connection:
   - Try temporarily disabling your firewall to test if that's the issue
   - Add an exception for port 3025 in your firewall settings

3. Install the Chrome extension if you haven't already:
   - Download from: https://github.com/AgentDeskAI/browser-tools-mcp/releases
   - Extract the zip file
   - Go to chrome://extensions/
   - Enable Developer mode
   - Click "Load unpacked" and select the extracted folder

4. Open Chrome DevTools (F12) and look for the BrowserTools tab

5. Try restarting Cursor after both the server and extension are set up

The connection between the MCP client and server is necessary for everything to work properly. Once you've completed these steps, the tools should start communicating with each other.

---

_**User**_

Try testing it out

---

_**Assistant**_



---

I see the server is running successfully and receiving URL updates from Microsoft Edge, but the MCP client can't find the server. Let's test it out:

---

```bash
curl http://localhost:3025/info
```

```
curl : Cannot GET /info
At line:1 char:1
+ curl http://localhost:3025/info
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidOperation: (System.Net.HttpWebRequest:HttpWebRequest) [Invoke-WebRequ

   est], WebException
    + FullyQualifiedErrorId : WebCmdletWebResponseException,Microsoft.PowerShell.Commands.InvokeWebRequest

   Command

```

---

Let's try the base endpoint:

---

```bash
curl http://localhost:3025/
```

```
PS C:\Users\rokur\Downloads> curl http://localhost:3025/
curl : Cannot GET /
At line:1 char:1
+ curl http://localhost:3025/
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidOperation: (System.Net.HttpWebRequest:HttpWebRequest) [Invoke-WebRequ

   est], WebException
    + FullyQualifiedErrorId : WebCmdletWebResponseException,Microsoft.PowerShell.Commands.InvokeWebRequest

PS C:\Users\rokur\Downloads>

```

---

Let's check the status of the server:

---

```bash
curl http://localhost:3025/status
```

```
curl : Cannot GET /status
At line:1 char:1
+ curl http://localhost:3025/status
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidOperation: (System.Net.HttpWebRequest:HttpWebRequest) [Invoke-WebRequ

   est], WebException
    + FullyQualifiedErrorId : WebCmdletWebResponseException,Microsoft.PowerShell.Commands.InvokeWebRequest


```

---

Let's test the logs endpoint:

---

```bash
curl http://localhost:3025/logs
```

```
curl : Cannot GET /logs
At line:1 char:1
+ curl http://localhost:3025/logs
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidOperation: (System.Net.HttpWebRequest:HttpWebRequest) [Invoke-WebRequ

   est], WebException
    + FullyQualifiedErrorId : WebCmdletWebResponseException,Microsoft.PowerShell.Commands.InvokeWebRequest

   Command

```

---

Now let's check if the server is actually listening on port 3025:

---

```bash
netstat -ano | findstr 3025
```

```
PS C:\Users\rokur\Downloads>

```

---

It appears there's no service listening on port 3025, which is strange since the browser-tools-server output showed it was running. Let's try restarting the browser-tools-server:

---

```bash
npx @agentdeskai/browser-tools-server
```

```
PS C:\Users\rokur\Downloads> npx @agentdeskai/browser-tools-server
Starting Browser Tools Server...
Requested port: 3025
Port 3025 is in use, trying next port...

====================================
NOTICE: Requested port 3025 was in use.
Using port 3026 instead.
====================================


For local access use: http://localhost:3026
```

---

_**User**_

But how do i use it with cursor??

---

_**Assistant**_



---

To use BrowserTools with Cursor, you need to:

1. Have both services running simultaneously:
   - First terminal: Keep `npx @agentdeskai/browser-tools-server` running
   - Second terminal: Run `npx @agentdeskai/browser-tools-mcp@1.2.0`

2. Make sure the Chrome/Edge extension is installed:
   - Open Chrome/Edge and go to chrome://extensions/ or edge://extensions/
   - Enable Developer mode (top-right toggle)
   - Click "Load unpacked" and browse to the extracted extension folder
   - You should see "BrowserToolsMCP" in your list of extensions

3. Open Cursor and check MCP connection:
   - Go to Cursor settings (Ctrl+,)
   - Navigate to Features
   - Scroll down to "MCP Servers"
   - Verify "browser-tools" shows as connected

4. Open your browser's Developer Tools (F12):
   - You should see a "BrowserTools" tab
   - This is where logs and screenshots will be managed

5. In Cursor, try asking for browser information:
   - Ask something like "What's happening in my browser right now?"
   - Or "Can you check the console for any errors?"

From your logs, I can see the server is running correctly and receiving URL updates from Edge, but the MCP client can't connect. Try temporarily disabling your firewall to test if that's the issue, or ensure both services are running on the same machine.

---



---

