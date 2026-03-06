// 主要JavaScript文件

document.addEventListener('DOMContentLoaded', function() {
    function ensureAIWidgetMarkup() {
        const hasToggle = document.getElementById('aiWidgetToggle');
        const hasChatWindow = document.getElementById('aiChatWindow');
        const hasModal = document.getElementById('apiKeyModal');
        if (hasToggle && hasChatWindow && hasModal) return;

        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <div class="ai-widget-toggle" id="aiWidgetToggle" title="咨询 AI 助手">
                <i class="fas fa-robot"></i>
            </div>

            <div class="api-key-modal" id="apiKeyModal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>配置 Kimi API Key</h3>
                        <button class="close-modal" id="closeApiModal">&times;</button>
                    </div>
                    <div class="modal-body">
                        <p>为了使用真实的 AI 对话功能，请输入您的 Moonshot API Key。</p>
                        <p class="api-note">您的 Key 仅存储在本地，不会发送给第三方。</p>
                        <input type="password" id="apiKeyInput" placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx">
                        <div class="modal-actions">
                            <button class="btn-cancel" id="cancelApiKey">使用模拟模式</button>
                            <button class="btn-save" id="saveApiKey">保存并启用</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="ai-chat-window" id="aiChatWindow">
                <div class="chat-header">
                    <div class="header-info">
                        <div class="ai-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="header-text">
                            <h3>信义智能助手</h3>
                            <span class="status-dot"></span>
                            <span class="status-text">Kimi 2.5 在线</span>
                        </div>
                    </div>
                    <button class="close-chat" id="closeChat">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="chat-messages" id="chatMessages">
                    <div class="message ai">
                        您好！我是信义企业管理的智能助手。有什么我可以帮您的吗？<br>
                        我可以回答关于体系认证、产品认证或政府项目申报的问题。
                    </div>
                </div>
                <div class="chat-input-area">
                    <input type="text" id="chatInput" placeholder="请输入您的问题..." autocomplete="off">
                    <button class="send-btn" id="sendBtn">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        `;
        while (wrapper.firstElementChild) {
            document.body.appendChild(wrapper.firstElementChild);
        }
    }

    ensureAIWidgetMarkup();

    // 移动端菜单切换
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav');

    if (menuToggle && nav) {
        menuToggle.addEventListener('click', function() {
            nav.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }

    // 滚动时导航栏效果
    const header = document.querySelector('header');
    if (header) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // FAQ 交互在 aiWidget 就绪后绑定（支持“点标题问AI / 点+展开答案”）

    // 平滑滚动到锚点
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });

    // 滚动动画效果
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight - 100) {
                element.classList.add('animated');
            }
        });
    };

    // 初始检查
    animateOnScroll();
    
    // 滚动时检查
    window.addEventListener('scroll', animateOnScroll);

    // AI 聊天助手逻辑
    const aiWidget = {
        toggle: document.getElementById('aiWidgetToggle'),
        window: document.getElementById('aiChatWindow'),
        closeBtn: document.getElementById('closeChat'),
        input: document.getElementById('chatInput'),
        sendBtn: document.getElementById('sendBtn'),
        messagesContainer: document.getElementById('chatMessages'),
        apiKeyModal: document.getElementById('apiKeyModal'),
        apiKeyInput: document.getElementById('apiKeyInput'),
        closeApiModalBtn: document.getElementById('closeApiModal'),
        cancelApiKeyBtn: document.getElementById('cancelApiKey'),
        saveApiKeyBtn: document.getElementById('saveApiKey'),
        apiKeyStorageKey: 'moonshot_api_key',
        apiPromptDismissKey: 'moonshot_api_prompt_dismissed_v1',
        historyStorageKey: 'ai_chat_history_v1',
        messageStorageKey: 'ai_chat_messages_v1',
        windowStateStorageKey: 'ai_chat_open_v1',
        lastActiveStorageKey: 'ai_chat_last_active_v1',
        defaultWelcomeText: '您好！我是信义企业管理的智能助手。有什么我可以帮您的吗？我可以回答关于体系认证、产品认证或政府项目申报的问题。',
        maxHistoryEntries: 20,
        maxMessageEntries: 80,
        sessionTimeoutMs: 30 * 60 * 1000,
        resetBtn: null,
        voiceBtn: null,
        recognition: null,
        isListening: false,

        init() {
            if (!this.toggle) return;
            if (!this.window || !this.closeBtn || !this.input || !this.sendBtn || !this.messagesContainer) {
                console.error('AI Widget 初始化失败：关键节点缺失');
                return;
            }

            const firstAiMsg = this.messagesContainer.querySelector('.message.ai');
            if (firstAiMsg && firstAiMsg.textContent) {
                this.defaultWelcomeText = firstAiMsg.textContent.replace(/\s+/g, ' ').trim();
            }

            this.history = this.loadHistory();
            this.messageLog = this.loadMessageLog();
            if (this.messageLog.length === 0) {
                this.messageLog = [{ type: 'ai', text: this.defaultWelcomeText }];
                this.saveMessageLog();
            }
            this.maybeResetByInactivity();
            this.renderStoredMessages();

            this.sessionId = localStorage.getItem('ai_chat_session_id');
            if (!this.sessionId) {
                this.sessionId = `sess_${Date.now()}_${Math.random().toString(16).slice(2, 8)}`;
                localStorage.setItem('ai_chat_session_id', this.sessionId);
            }

            this.bindApiKeyModal();
            this.ensureResetButton();
            this.bindResetButton();
            this.ensureVoiceButton();
            this.initSpeechRecognition();

            this.toggle.addEventListener('click', () => {
                this.toggleChatWindow();
            });
            this.closeBtn.addEventListener('click', () => {
                this.closeChatWindow();
            });

            const handleSend = () => {
                const text = this.input.value.trim();
                if (text) {
                    this.addMessage(text, 'user');
                    this.input.value = '';
                    this.showTyping();
                    setTimeout(() => {
                        this.sendMessage(text);
                    }, 300);
                }
            };

            this.sendBtn.addEventListener('click', handleSend);
            this.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') handleSend();
            });

            this.restoreChatWindowState();
        },

        safeParseArray(raw) {
            if (!raw) return [];
            try {
                const parsed = JSON.parse(raw);
                return Array.isArray(parsed) ? parsed : [];
            } catch (_) {
                return [];
            }
        },

        loadHistory() {
            const data = this.safeParseArray(localStorage.getItem(this.historyStorageKey));
            return data.filter((item) => {
                return item && (item.role === 'user' || item.role === 'assistant') && typeof item.content === 'string' && item.content.trim();
            }).slice(-this.maxHistoryEntries);
        },

        saveHistory() {
            localStorage.setItem(this.historyStorageKey, JSON.stringify(this.history.slice(-this.maxHistoryEntries)));
        },

        loadMessageLog() {
            const data = this.safeParseArray(localStorage.getItem(this.messageStorageKey));
            return data.filter((item) => {
                return item && (item.type === 'user' || item.type === 'ai') && typeof item.text === 'string' && item.text.trim();
            }).slice(-this.maxMessageEntries);
        },

        saveMessageLog() {
            localStorage.setItem(this.messageStorageKey, JSON.stringify(this.messageLog.slice(-this.maxMessageEntries)));
        },

        renderStoredMessages() {
            this.messagesContainer.innerHTML = '';
            this.messageLog.forEach((msg) => {
                this.appendMessageNode(msg.text, msg.type);
            });
            this.scrollToBottom();
        },

        appendMessageNode(text, type) {
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${type}`;
            msgDiv.textContent = text;
            this.messagesContainer.appendChild(msgDiv);
        },

        openChatWindow(persist = true) {
            this.window.classList.add('active');
            if (persist) localStorage.setItem(this.windowStateStorageKey, '1');
            this.touchActive();
            // 在移动端隐藏悬浮球
            if (window.innerWidth <= 480) {
                this.toggle.classList.add('hidden');
            }
            this.input.focus();
            this.scrollToBottom();
            this.promptApiKeyIfNeeded();
        },

        closeChatWindow(persist = true) {
            this.window.classList.remove('active');
            // 恢复显示悬浮球
            this.toggle.classList.remove('hidden');
            if (persist) localStorage.setItem(this.windowStateStorageKey, '0');
            this.touchActive();
            if (this.isListening) this.stopVoiceInput();
        },

        toggleChatWindow() {
            if (this.window.classList.contains('active')) {
                this.closeChatWindow();
                this.toggle.classList.remove('hidden'); // 显示悬浮球
            } else {
                this.openChatWindow();
                // 在移动端隐藏悬浮球，防止遮挡
                if (window.innerWidth <= 480) {
                    this.toggle.classList.add('hidden');
                }
            }
        },

        restoreChatWindowState() {
            // 移动端不自动恢复打开状态，以免遮挡屏幕
            if (window.innerWidth <= 480) return;
            
            if (localStorage.getItem(this.windowStateStorageKey) === '1') {
                this.openChatWindow(false);
            } else {
                this.closeChatWindow(false);
            }
        },

        touchActive(ts = Date.now()) {
            localStorage.setItem(this.lastActiveStorageKey, String(ts));
        },

        maybeResetByInactivity() {
            const now = Date.now();
            const lastActive = Number(localStorage.getItem(this.lastActiveStorageKey) || '0');
            if (lastActive > 0 && now - lastActive > this.sessionTimeoutMs) {
                this.resetConversation(false);
            }
            this.touchActive(now);
        },

        resetConversation(withNotice = true) {
            this.history = [];
            this.saveHistory();
            this.messageLog = [{ type: 'ai', text: this.defaultWelcomeText }];
            this.saveMessageLog();
            this.sessionId = `sess_${Date.now()}_${Math.random().toString(16).slice(2, 8)}`;
            localStorage.setItem('ai_chat_session_id', this.sessionId);
            this.renderStoredMessages();
            this.removeTyping();
            this.touchActive();
            if (withNotice) {
                this.addMessage('已开启新对话，我们从头开始。', 'ai');
            }
        },

        ensureResetButton() {
            const chatHeader = this.window.querySelector('.chat-header');
            if (!chatHeader || !this.closeBtn) return;
            let btn = document.getElementById('resetChat');
            if (!btn) {
                btn = document.createElement('button');
                btn.type = 'button';
                btn.id = 'resetChat';
                btn.className = 'reset-chat-btn';
                btn.title = '新建对话';
                btn.setAttribute('aria-label', '新建对话');
                btn.innerHTML = '<i class="fas fa-redo-alt"></i>';
                this.closeBtn.parentNode.insertBefore(btn, this.closeBtn);
            }
            this.resetBtn = btn;
        },

        bindResetButton() {
            if (!this.resetBtn) return;
            this.resetBtn.addEventListener('click', () => {
                this.resetConversation(true);
                this.input.focus();
            });
        },

        ensureVoiceButton() {
            const inputArea = this.window.querySelector('.chat-input-area');
            if (!inputArea) return;
            let btn = document.getElementById('voiceBtn');
            if (!btn) {
                btn = document.createElement('button');
                btn.type = 'button';
                btn.id = 'voiceBtn';
                btn.className = 'voice-btn';
                btn.title = '语音输入';
                btn.setAttribute('aria-label', '语音输入');
                btn.innerHTML = '<i class="fas fa-microphone"></i>';
                inputArea.insertBefore(btn, this.sendBtn);
            }
            this.voiceBtn = btn;
        },

        initSpeechRecognition() {
            if (!this.voiceBtn) return;
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                this.voiceBtn.disabled = true;
                this.voiceBtn.title = '当前浏览器不支持语音输入';
                return;
            }

            this.recognition = new SpeechRecognition();
            this.recognition.lang = 'zh-CN';
            this.recognition.continuous = false;
            this.recognition.interimResults = true;
            this.recognition.maxAlternatives = 1;

            let baseText = '';
            this.recognition.onstart = () => {
                this.isListening = true;
                baseText = this.input.value.trim();
                if (baseText) baseText += ' ';
                this.updateVoiceButton();
            };

            this.recognition.onresult = (event) => {
                let finalText = '';
                let interimText = '';
                for (let i = event.resultIndex; i < event.results.length; i += 1) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalText += transcript;
                    } else {
                        interimText += transcript;
                    }
                }
                this.input.value = `${baseText}${finalText}${interimText}`.trim();
            };

            this.recognition.onerror = (event) => {
                if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
                    this.addMessage('语音输入权限被拒绝，请在浏览器中允许麦克风权限。', 'ai');
                } else if (event.error !== 'no-speech') {
                    this.addMessage(`语音识别失败：${event.error}`, 'ai');
                }
            };

            this.recognition.onend = () => {
                this.isListening = false;
                this.updateVoiceButton();
                this.input.focus();
            };

            this.voiceBtn.addEventListener('click', () => {
                this.toggleVoiceInput();
            });
            this.updateVoiceButton();
        },

        toggleVoiceInput() {
            if (!this.recognition) return;
            if (this.isListening) {
                this.stopVoiceInput();
                return;
            }
            this.recognition.start();
        },

        stopVoiceInput() {
            if (!this.recognition) return;
            try {
                this.recognition.stop();
            } catch (_) {
                // ignore stop errors when recognition is already inactive
            }
        },

        updateVoiceButton() {
            if (!this.voiceBtn) return;
            this.voiceBtn.classList.toggle('listening', this.isListening);
            this.voiceBtn.title = this.isListening ? '停止语音输入' : '语音输入';
            this.voiceBtn.innerHTML = this.isListening
                ? '<i class="fas fa-microphone-slash"></i>'
                : '<i class="fas fa-microphone"></i>';
        },

        getSavedClientApiKey() {
            return (localStorage.getItem(this.apiKeyStorageKey) || '').trim();
        },

        bindApiKeyModal() {
            if (!this.apiKeyModal) return;

            const closeWithMock = () => {
                localStorage.setItem(this.apiPromptDismissKey, '1');
                this.closeApiKeyModal();
            };

            if (this.closeApiModalBtn) {
                this.closeApiModalBtn.addEventListener('click', closeWithMock);
            }
            if (this.cancelApiKeyBtn) {
                this.cancelApiKeyBtn.addEventListener('click', closeWithMock);
            }
            if (this.saveApiKeyBtn) {
                this.saveApiKeyBtn.addEventListener('click', () => {
                    const key = (this.apiKeyInput?.value || '').trim();
                    if (!key) {
                        if (this.apiKeyInput) this.apiKeyInput.focus();
                        return;
                    }
                    localStorage.setItem(this.apiKeyStorageKey, key);
                    localStorage.removeItem(this.apiPromptDismissKey);
                    this.closeApiKeyModal();
                    this.addMessage('API Key 已保存，正在连接 Kimi AI...', 'ai');
                });
            }

            this.apiKeyModal.addEventListener('click', (e) => {
                if (e.target === this.apiKeyModal) {
                    closeWithMock();
                }
            });
        },

        openApiKeyModal() {
            if (!this.apiKeyModal) return;
            this.apiKeyModal.classList.add('active');
            if (this.apiKeyInput) {
                this.apiKeyInput.value = this.getSavedClientApiKey();
                setTimeout(() => this.apiKeyInput.focus(), 50);
            }
        },

        closeApiKeyModal() {
            if (!this.apiKeyModal) return;
            this.apiKeyModal.classList.remove('active');
        },

        promptApiKeyIfNeeded(force = false) {
            if (!this.apiKeyModal) return;
            const hasSavedKey = !!this.getSavedClientApiKey();
            if (hasSavedKey) return;
            if (!force && localStorage.getItem(this.apiPromptDismissKey) === '1') return;
            this.openApiKeyModal();
        },

        async sendMessage(text) {
            try {
                this.touchActive();
                const savedClientKey = this.getSavedClientApiKey();
                const headers = {
                    'Content-Type': 'application/json'
                };
                if (savedClientKey) {
                    headers['X-API-Key'] = savedClientKey;
                }

                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers,
                    body: JSON.stringify({
                        message: text,
                        history: this.history,
                        session_id: this.sessionId
                    })
                });

                const data = await response.json();
                this.removeTyping();

                if (!response.ok) {
                    const errMsg = data.error || '服务暂时不可用';
                    const detail = data.detail ? `（${data.detail}）` : '';
                    this.addMessage(`连接失败：${errMsg}${detail}`, 'ai');
                    const diagnoseText = `${errMsg} ${data.detail || ''}`.toLowerCase();
                    if (
                        diagnoseText.includes('moonshot_api_key') ||
                        diagnoseText.includes('api key') ||
                        diagnoseText.includes('unauthorized') ||
                        diagnoseText.includes('invalid')
                    ) {
                        this.promptApiKeyIfNeeded(true);
                    }
                    this.mockAIResponse(text);
                    return;
                }

                if (data.session_id && data.session_id !== this.sessionId) {
                    this.sessionId = data.session_id;
                    localStorage.setItem('ai_chat_session_id', this.sessionId);
                }

                let aiReply = '';
                if (data.reply) {
                    aiReply = data.reply;
                } else if (data.choices && data.choices[0] && data.choices[0].message) {
                    aiReply = data.choices[0].message.content || '';
                }

                if (aiReply) {
                    this.addMessage(aiReply, 'ai');
                    this.history.push({ role: 'user', content: text });
                    this.history.push({ role: 'assistant', content: aiReply });
                    if (this.history.length > this.maxHistoryEntries) {
                        this.history = this.history.slice(-this.maxHistoryEntries);
                    }
                    this.saveHistory();
                } else {
                    this.mockAIResponse(text);
                }
            } catch (error) {
                console.error('Network Error:', error);
                this.removeTyping();
                this.addMessage('网络连接异常，请检查您的网络设置。', 'ai');
                this.mockAIResponse(text);
            }
        },

        addMessage(text, type, persist = true) {
            const cleanText = (text || '').toString().trim();
            if (!cleanText) return;
            this.appendMessageNode(cleanText, type);
            if (persist) {
                this.messageLog.push({ type, text: cleanText });
                if (this.messageLog.length > this.maxMessageEntries) {
                    this.messageLog = this.messageLog.slice(-this.maxMessageEntries);
                }
                this.saveMessageLog();
            }
            this.touchActive();
            this.scrollToBottom();
        },

        showTyping() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'typing-indicator';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = `
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            `;
            this.messagesContainer.appendChild(typingDiv);
            this.scrollToBottom();
        },

        removeTyping() {
            const indicator = document.getElementById('typingIndicator');
            if (indicator) indicator.remove();
        },

        scrollToBottom() {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        },

        mockAIResponse(userText) {
            let reply = '抱歉，我暂时无法回答这个问题。您可以拨打我们的热线：+86 13676797588';

            if (userText.includes('认证') || userText.includes('体系')) {
                reply = '我们提供 ISO9001、ISO14001 等多种体系认证服务。需要具体报价吗？';
            } else if (userText.includes('你好') || userText.includes('在吗')) {
                reply = '您好！我是信义智能助手，很高兴为您服务。';
            } else if (userText.includes('价格') || userText.includes('多少钱')) {
                reply = '具体费用根据企业规模而定，建议您留下联系方式，我们的顾问会为您详细评估。';
            }

            this.addMessage(reply, 'ai');
        }
    };
    
    aiWidget.ask = function ask(questionText, options = {}) {
        const text = (questionText || '').toString().trim();
        if (!text) return;

        const autoSend = options.autoSend !== false;
        const hasKey = !!this.getSavedClientApiKey();

        this.openChatWindow();
        if (this.input) {
            this.input.value = text;
            this.input.focus();
        }

        // 没有 Key 时先让用户保存 Key，再由用户手动发送，避免“连接失败”的挫败感。
        if (!autoSend || !hasKey) return;

        this.addMessage(text, 'user');
        if (this.input) this.input.value = '';
        this.showTyping();
        setTimeout(() => this.sendMessage(text), 300);
    };

    // FAQ：点标题问 AI，点“+”展开/收起答案
    const faqItems = document.querySelectorAll('.faq-item');
    if (faqItems.length > 0) {
        const closeOtherFaqItems = (currentItem) => {
            faqItems.forEach((otherItem) => {
                if (otherItem !== currentItem && otherItem.classList.contains('active')) {
                    otherItem.classList.remove('active');
                    const icon = otherItem.querySelector('.toggle-icon i');
                    if (icon) icon.className = 'fas fa-plus';
                }
            });
        };

        const toggleFaqItem = (item) => {
            closeOtherFaqItems(item);
            item.classList.toggle('active');
            const icon = item.querySelector('.toggle-icon i');
            if (!icon) return;
            icon.className = item.classList.contains('active') ? 'fas fa-minus' : 'fas fa-plus';
        };

        faqItems.forEach((item) => {
            const questionEl = item.querySelector('.faq-question');
            if (!questionEl) return;
            const toggleEl = questionEl.querySelector('.toggle-icon');

            if (toggleEl) {
                toggleEl.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    toggleFaqItem(item);
                });
            }

            questionEl.addEventListener('click', (e) => {
                if (e.target && e.target.closest && e.target.closest('.toggle-icon')) return;
                const h3 = questionEl.querySelector('h3');
                const questionText = (h3?.textContent || '').trim();
                aiWidget.ask(questionText, { autoSend: true });
            });
        });
    }

    // FAQ “继续问智能助手”按钮
    document.querySelectorAll('.faq-ask-ai').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const questionText = btn.getAttribute('data-ask') || '';
            aiWidget.ask(questionText, { autoSend: true });
        });
    });

    // 支持跨页面跳转：?ask=xxx 打开机器人并带入问题（有 Key 则自动发送）
    try {
        const params = new URLSearchParams(window.location.search);
        const ask = (params.get('ask') || '').trim();
        if (ask) {
            aiWidget.ask(ask, { autoSend: true });
        }
    } catch (_) {
        // ignore URLSearchParams issues
    }

    // 暴露一个轻量入口，方便其它页面/按钮直接调用
    window.XINYI_AI = {
        open: () => aiWidget.openChatWindow(),
        ask: (text, options) => aiWidget.ask(text, options),
        reset: () => aiWidget.resetConversation(true),
    };

    aiWidget.init();
});
