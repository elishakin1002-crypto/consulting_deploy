// 主要JavaScript文件

document.addEventListener('DOMContentLoaded', function() {
    function ensureAIWidgetMarkup() {
        const hasToggle = document.getElementById('aiWidgetToggle');
        const hasChatWindow = document.getElementById('aiChatWindow');
        if (hasToggle && hasChatWindow) return;

        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <div class="ai-widget-toggle" id="aiWidgetToggle" title="智能咨询">
                <i class="fas fa-robot"></i>
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
                            <span class="status-text">在线</span>
                        </div>
                    </div>
                    <button class="close-chat" id="closeChat">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="chat-messages" id="chatMessages">
                    <div class="message ai">
                        您好！我是信义智能助手。有什么我可以帮您的吗？<br>
                        我可以为您梳理认证/许可办理顺序、资料清单与周期预估。
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
        historyStorageKey: 'ai_chat_history_v1',
        messageStorageKey: 'ai_chat_messages_v1',
        leadStorageKey: 'ai_chat_lead_profile_v1',
        leadAckStorageKey: 'ai_chat_lead_ack_v1',
        windowStateStorageKey: 'ai_chat_open_v1',
        lastActiveStorageKey: 'ai_chat_last_active_v1',
        defaultWelcomeText: '您好！我是信义智能助手。有什么我可以帮您的吗？我可以为您梳理认证/许可办理顺序、资料清单与周期预估。',
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
            this.leadProfile = this.loadLeadProfile();
            // 清理旧版遗留本地数据，避免影响当前对话流程。
            Object.keys(localStorage).forEach((key) => {
                if (/(_api_key$)|(^api_key$)|(_api_prompt_dismissed(_v\d+)?$)/i.test(key)) {
                    localStorage.removeItem(key);
                }
            });
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

        loadLeadProfile() {
            try {
                const raw = localStorage.getItem(this.leadStorageKey);
                if (!raw) return {};
                const parsed = JSON.parse(raw);
                return parsed && typeof parsed === 'object' ? parsed : {};
            } catch (_) {
                return {};
            }
        },

        saveLeadProfile() {
            localStorage.setItem(this.leadStorageKey, JSON.stringify(this.leadProfile || {}));
        },

        extractLeadFields(text) {
            const content = (text || '').trim();
            if (!content) return {};
            const lead = {};
            const phoneMatch = content.match(/(?:\+?86[-\s]?)?(1[3-9]\d{9})/);
            if (phoneMatch) lead.phone = phoneMatch[1];
            const emailMatch = content.match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/);
            if (emailMatch) lead.email = emailMatch[0];
            const nameMatch = content.match(/(?:我叫|我是|联系人[:：]?)([^\s，。,.]{2,16})/);
            if (nameMatch) lead.contact_name = nameMatch[1];
            return lead;
        },

        buildLeadSignature(lead) {
            if (!lead || typeof lead !== 'object') return '';
            const phone = (lead.phone || '').trim();
            const email = (lead.email || '').trim();
            const name = (lead.contact_name || '').trim();
            return [name, phone, email].join('|');
        },

        mergeLeadProfile(partialLead) {
            const merged = { ...(this.leadProfile || {}) };
            if (partialLead && typeof partialLead === 'object') {
                Object.keys(partialLead).forEach((key) => {
                    const value = partialLead[key];
                    if (typeof value === 'string' && value.trim()) {
                        merged[key] = value.trim();
                    }
                });
            }
            this.leadProfile = merged;
            this.saveLeadProfile();
            return merged;
        },

        maybeAcknowledgeLeadCapture(lead, triggerText = '') {
            if (!lead || typeof lead !== 'object') return;
            const hasContact = !!(lead.phone || lead.email);
            if (!hasContact) return;

            const userProvided = this.extractLeadFields(triggerText);
            if (!userProvided.phone && !userProvided.email && !userProvided.contact_name) return;

            const signature = this.buildLeadSignature(lead);
            if (!signature) return;
            if (localStorage.getItem(this.leadAckStorageKey) === signature) return;

            const contactBits = [];
            if (lead.contact_name) contactBits.push(`姓名：${lead.contact_name}`);
            if (lead.phone) contactBits.push(`电话：${lead.phone}`);
            if (lead.email) contactBits.push(`邮箱：${lead.email}`);
            this.addMessage(`已收到并记录您的联系方式（${contactBits.join('，')}）。顾问将尽快与您联系。`, 'ai');
            localStorage.setItem(this.leadAckStorageKey, signature);
        },

        startFreeConsultFlow() {
            this.openChatWindow();
            const leadPrompt = '免费咨询已开启。请直接输入【姓名 + 电话（或微信/邮箱）+ 需求】，我会立即为您登记并安排顾问联系。';
            const lastMessage = this.messageLog.length ? this.messageLog[this.messageLog.length - 1] : null;
            if (!lastMessage || lastMessage.type !== 'ai' || lastMessage.text !== leadPrompt) {
                this.addMessage(leadPrompt, 'ai');
            }
            if (this.input) {
                this.input.placeholder = '例如：我叫张三，电话138xxxx8888，想办SC食品生产许可';
                this.input.focus();
            }
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
            
            // 关键：在移动端，打开窗口时强制隐藏悬浮球
            if (window.innerWidth <= 480 && this.toggle) {
                this.toggle.classList.add('hidden');
                this.toggle.style.display = 'none'; // 强制内联样式隐藏
            }

            this.touchActive();
            this.input.focus();
            this.scrollToBottom();
        },

        closeChatWindow(persist = true) {
            this.window.classList.remove('active');
            
            // 恢复悬浮球显示
            if (this.toggle) {
                this.toggle.classList.remove('hidden');
                this.toggle.style.display = ''; // 清除内联样式
            }

            if (persist) localStorage.setItem(this.windowStateStorageKey, '0');
            this.touchActive();
            if (this.isListening) this.stopVoiceInput();
        },

        toggleChatWindow() {
            if (this.window.classList.contains('active')) {
                this.closeChatWindow();
            } else {
                this.openChatWindow();
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

        async sendMessage(text) {
            try {
                this.touchActive();
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
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
                    // const detail = data.detail ? `（${data.detail}）` : '';
                    // this.addMessage(`连接失败：${errMsg}${detail}`, 'ai');
                    this.addMessage('系统升级中，请稍后再试。', 'ai');
                    
                    const diagnoseText = `${errMsg} ${data.detail || ''}`.toLowerCase();
                    const isEngineBusy = diagnoseText.includes('engine_overloaded') || diagnoseText.includes('overloaded') || diagnoseText.includes('繁忙');
                    if (isEngineBusy || response.status >= 500) return;
                    return;
                }

                if (data.session_id && data.session_id !== this.sessionId) {
                    this.sessionId = data.session_id;
                    localStorage.setItem('ai_chat_session_id', this.sessionId);
                }

                const aiReply = typeof data.reply === 'string' ? data.reply : '';

                if (aiReply) {
                    this.addMessage(aiReply, 'ai');
                    this.history.push({ role: 'user', content: text });
                    this.history.push({ role: 'assistant', content: aiReply });
                    if (this.history.length > this.maxHistoryEntries) {
                        this.history = this.history.slice(-this.maxHistoryEntries);
                    }
                    this.saveHistory();
                    const mergedLead = this.mergeLeadProfile({
                        ...this.extractLeadFields(text),
                        ...(data && data.sales && typeof data.sales.lead_profile === 'object' ? data.sales.lead_profile : {}),
                    });
                    this.maybeAcknowledgeLeadCapture(mergedLead, text);
                } else {
                    this.addMessage('暂未获取到有效回复，请稍后重试。', 'ai');
                }
            } catch (error) {
                console.error('Network Error:', error);
                this.removeTyping();
                this.addMessage('网络连接异常，请检查您的网络设置。', 'ai');
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

    };
    
    aiWidget.ask = function ask(questionText, options = {}) {
        const text = (questionText || '').toString().trim();
        if (!text) return;

        const autoSend = options.autoSend !== false;

        this.openChatWindow();
        if (this.input) {
            this.input.value = text;
            this.input.focus();
        }

        if (!autoSend) return;

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

    // 支持跨页面跳转：?ask=xxx 打开机器人并带入问题后自动发送
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
        startConsult: () => aiWidget.startFreeConsultFlow(),
        reset: () => aiWidget.resetConversation(true),
    };

    // 首页“免费咨询”直接进入机器人留资流程
    document.querySelectorAll('.js-open-ai-consult').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            aiWidget.startFreeConsultFlow();
        });
    });

    aiWidget.init();
});
