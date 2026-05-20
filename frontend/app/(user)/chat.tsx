// app/(user)/chat.tsx
import { useEffect, useState, useRef } from 'react';
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  TouchableWithoutFeedback,
  Platform,
  ScrollView,
  Alert,
  StyleSheet,
} from 'react-native';
import { router } from 'expo-router';
import { chatAPI, notificationsAPI } from '@/lib/api';
import ProviderCard from '@/components/ProviderCard';
import { Feather } from '@expo/vector-icons';

interface Message {
  id: string;
  role: 'user' | 'bot';
  content: string;
  providers?: Provider[];
  trace?: string;
  needsClarification?: boolean;
}

interface Provider {
  id: string;
  name: string;
  service_type: string;
  rating: number;
  eta_minutes: number;
  rate_per_hour: number;
  match_score: number;
  is_available: boolean;
  area?: string;
}

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loadingSend, setLoadingSend] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  const showWelcomeMessage = () => {
    setMessages([
      {
        id: 'welcome',
        role: 'bot',
        content: 'Assalam o Alaikum! Kaunsi service chahiye?\nUrdu ya English mein batao',
      },
    ]);
  };

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await chatAPI.history() as any;
        if (data && data.length) {
          setMessages(data);
        } else {
          showWelcomeMessage();
        }
      } catch (e) {
        showWelcomeMessage();
      }
    };

    const fetchUnread = async () => {
      try {
        const notes = await notificationsAPI.list() as any;
        const count =
          notes.notifications?.filter((n: any) => !n.is_read).length || 0;
        setUnreadCount(count);
      } catch (_) {}
    };

    fetchHistory();
    fetchUnread();
  }, []);

  const addMessage = (msg: Message) => {
    setMessages((prev) => [...prev, msg]);
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    };

    addMessage(userMsg);
    setInput('');
    setLoadingSend(true);

    const typingMsg: Message = {
      id: 'typing',
      role: 'bot',
      content: '...',
    };
    addMessage(typingMsg);

    try {
      const response = await chatAPI.send(userMsg.content) as any;
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: response.reply || response.message || 'Kuch masla aa gaya.',
        providers: response.providers,
        trace: response.agent_trace,
        needsClarification: response.needs_clarification,
      };
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== 'typing'),
        botMsg,
      ]);
    } catch (e: any) {
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== 'typing'),
        {
          id: (Date.now() + 1).toString(),
          role: 'bot',
          content: e.message || 'Kuch masla aa gaya. Dobara try karo.',
        },
      ]);
    } finally {
      setLoadingSend(false);
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  };

  const handleClearHistory = () => {
    Alert.alert(
      'Chat Delete Karo?',
      'Kya aap poori chat history delete karna chahte hain?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await chatAPI.clearHistory();
              setMessages([]);
              showWelcomeMessage();
            } catch (e: any) {
              Alert.alert('Error', 'Delete nahi hua');
            }
          },
        },
      ]
    );
  };

  const handleNewConversation = () => {
    Alert.alert(
      'Naya Chat Shuru Karo?',
      'Current chat screen clear ho jayegi',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'New Chat',
          onPress: () => {
            setMessages([]);
            showWelcomeMessage();
          },
        },
      ]
    );
  };

  const renderMessage = ({ item }: { item: Message }) => {
    // User message
    if (item.role === 'user') {
      return (
        <View style={styles.userMsgWrapper}>
          <View style={styles.userBubble}>
            <Text style={styles.userText}>{item.content}</Text>
          </View>
          <Text style={styles.userLabel}>You</Text>
        </View>
      );
    }

    // Typing indicator
    if (item.content === '...') {
      return (
        <View style={styles.botMsgWrapper}>
          <View style={styles.typingBubble}>
            <ActivityIndicator size="small" color="#10b981" />
            <Text style={styles.typingText}>Karoo soch raha hai...</Text>
          </View>
        </View>
      );
    }

    // Bot message
    return (
      <View style={styles.botMsgWrapper}>
        <View style={styles.botBubble}>
          <Text style={styles.botText}>{item.content}</Text>
        </View>
          <Text style={styles.botLabel}>Karoo AI</Text>

        {/* Provider cards */}
        {item.providers && item.providers.length > 0 && (
          <View style={styles.providersWrapper}>
            <Text style={styles.providersTitle}>
              {item.providers.length} Provider
              {item.providers.length > 1 ? 's' : ''} Mil Gaye
            </Text>
            {item.providers.map((p) => (
              <ProviderCard
                key={p.id}
                provider={p}
                match_score={p.match_score}
                hideActions={true}
              />
            ))}
          </View>
        )}

        {/* Agent trace */}
        {item.trace && <TraceCollapsible trace={item.trace} />}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <View style={styles.aiAvatar}>
            <Feather name="cpu" size={20} color="#fff" />
          </View>
          <View>
            <Text style={styles.headerTitle}>Karoo AI</Text>
            <Text style={styles.headerSubtitle}>
              Powered by Google Gemini
            </Text>
          </View>
        </View>

        <View style={styles.headerActions}>
          <TouchableOpacity
            onPress={handleClearHistory}
            style={styles.headerBtn}
            accessibilityLabel="Clear chat history"
          >
            <Feather name="trash-2" size={18} color="#ef4444" />
          </TouchableOpacity>

          <TouchableOpacity
            onPress={handleNewConversation}
            style={[styles.headerBtn, { marginLeft: 8 }]}
            accessibilityLabel="New conversation"
          >
            <Feather name="plus-circle" size={18} color="#10b981" />
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => router.push('/(user)/notifications')}
            style={[styles.headerBtn, { marginLeft: 8 }]}
            accessibilityLabel="Notifications"
          >
            <Feather name="bell" size={20} color="#10b981" />
            {unreadCount > 0 && (
              <View style={styles.badge}>
                <Text style={styles.badgeText}>{unreadCount}</Text>
              </View>
            )}
          </TouchableOpacity>
        </View>
      </View>

      {/* Messages */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ padding: 12, paddingBottom: 20 }}
        showsVerticalScrollIndicator={false}
        onContentSizeChange={() =>
          flatListRef.current?.scrollToEnd({ animated: true })
        }
      />

      {/* Input bar */}
      <View style={styles.inputBar}>
        <TextInput
          placeholder="Urdu ya English mein likhein..."
          placeholderTextColor="#6b7280"
          style={styles.input}
          value={input}
          onChangeText={setInput}
          onSubmitEditing={handleSend}
          multiline
          maxLength={500}
        />
        <TouchableOpacity
          style={[
            styles.sendBtn,
            { backgroundColor: input.trim() && !loadingSend ? '#059669' : '#374151' },
          ]}
          onPress={handleSend}
          disabled={loadingSend || !input.trim()}
          accessibilityLabel="Send message"
        >
          {loadingSend ? (
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <Feather name="send" size={20} color="#fff" />
          )}
        </TouchableOpacity>
      </View>

      <Text style={styles.poweredBy}>
        Powered by Google Gemini • Multilingual AI
      </Text>
    </View>
  );
}

// ---------- Trace Collapsible ----------
function TraceCollapsible({ trace }: { trace: string }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <View style={{ marginTop: 8 }}>
      <TouchableWithoutFeedback onPress={() => setExpanded(!expanded)}>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <Feather name="search" size={14} color="#10b981" />
          <Text style={{ marginLeft: 4, color: '#10b981', fontSize: 13 }}>
            AI Reasoning dekho
          </Text>
        </View>
      </TouchableWithoutFeedback>

      {expanded && (
        <ScrollView
          style={{
            backgroundColor: '#1f2937',
            borderRadius: 8,
            padding: 8,
            marginTop: 4,
            maxHeight: 160,
          }}
        >
          <Text style={{ fontSize: 11, color: '#e5e7eb', fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace' }}>
            {trace}
          </Text>
        </ScrollView>
      )}
    </View>
  );
}

// ---------- Styles ----------
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#030712',
  },
  header: {
    backgroundColor: '#111827',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(16,185,129,0.2)',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  aiAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#059669',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  headerTitle: {
    color: '#10b981',
    fontSize: 18,
    fontWeight: 'bold',
  },
  headerSubtitle: {
    color: '#6b7280',
    fontSize: 11,
    marginTop: 2,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerBtn: {
    padding: 8,
    backgroundColor: 'rgba(16,185,129,0.1)',
    borderRadius: 8,
  },
  badge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: '#ef4444',
    borderRadius: 10,
    width: 18,
    height: 18,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: '#111827',
  },
  badgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  userMsgWrapper: {
    alignSelf: 'flex-end',
    maxWidth: '80%',
    marginBottom: 12,
    alignItems: 'flex-end',
  },
  userBubble: {
    backgroundColor: '#059669',
    borderRadius: 20,
    borderBottomRightRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  userText: {
    color: '#ffffff',
    fontSize: 15,
    lineHeight: 22,
  },
  userLabel: {
    color: '#6b7280',
    fontSize: 11,
    marginTop: 4,
  },
  botMsgWrapper: {
    alignSelf: 'flex-start',
    maxWidth: '85%',
    marginBottom: 12,
  },
  botBubble: {
    backgroundColor: '#1f2937',
    borderRadius: 20,
    borderBottomLeftRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: '#374151',
  },
  botText: {
    color: '#ffffff',
    fontSize: 15,
    lineHeight: 22,
  },
  botLabel: {
    color: '#6b7280',
    fontSize: 11,
    marginTop: 4,
  },
  typingBubble: {
    backgroundColor: '#1f2937',
    borderRadius: 20,
    borderBottomLeftRadius: 4,
    paddingHorizontal: 16,
    paddingVertical: 12,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#374151',
  },
  typingText: {
    color: '#9ca3af',
    fontSize: 13,
    marginLeft: 8,
  },
  providersWrapper: {
    marginTop: 10,
  },
  providersTitle: {
    color: '#10b981',
    fontWeight: '600',
    fontSize: 13,
    marginBottom: 6,
  },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: '#111827',
    borderTopWidth: 1,
    borderTopColor: '#1f2937',
    gap: 8,
  },
  input: {
    flex: 1,
    backgroundColor: '#1f2937',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    color: '#ffffff',
    fontSize: 15,
    maxHeight: 120,
    borderWidth: 1,
    borderColor: '#374151',
  },
  sendBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
  },
  poweredBy: {
    color: '#4b5563',
    fontSize: 11,
    textAlign: 'center',
    paddingBottom: 8,
    backgroundColor: '#111827',
  },
});