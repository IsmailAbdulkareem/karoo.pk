// app/(user)/chat.tsx
import { useEffect, useState, useRef } from 'react';
import { View, Text, FlatList, TextInput, TouchableOpacity, ActivityIndicator, TouchableWithoutFeedback, LayoutAnimation, UIManager, Platform, ScrollView, Alert } from 'react-native';
import { router } from 'expo-router';
import { chatAPI, notificationsAPI } from '@/lib/api';
import { storage } from '@/lib/storage';
import ProviderCard from '@/components/ProviderCard';
import { Feather } from '@expo/vector-icons';

// Enable LayoutAnimation on Android
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

interface Message {
  id: string;
  role: 'user' | 'bot';
  content: string;
  // optional extra data for bot messages
  providers?: Provider[];
  // for debug trace
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
  match_score: number; // 0-1
  is_available: boolean;
  area?: string;
}

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loadingSend, setLoadingSend] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const flatListRef = useRef<FlatList>(null);

  // Show welcome message
  const showWelcomeMessage = () => {
    setMessages([{
      id: 'welcome',
      role: 'bot',
      content: 'Assalam o Alaikum! 👋 Kaunsi service chahiye?\nUrdu ya English mein batao',
    }]);
  };

  // Load chat history on mount
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await chatAPI.history();
        // API is expected to return array of {id, role, content, ...}
        if (data && data.length) {
          setMessages(data); // oldest to newest (ascending)
        } else {
          // No history, show welcome message
          showWelcomeMessage();
        }
      } catch (e) {
        console.error('Chat history load error', e);
        showWelcomeMessage();
      }
    };
    fetchHistory();
    // fetch unread notifications count
    const fetchUnread = async () => {
      try {
        const notes = await notificationsAPI.list();
        const count = notes.notifications?.filter((n: any) => !n.is_read).length || 0;
        setUnreadCount(count);
      } catch (_) {}
    };
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
    // show typing indicator as a bot message with placeholder
    const typingMsg: Message = {
      id: 'typing',
      role: 'bot',
      content: '...', // will be replaced
    };
    addMessage(typingMsg);
    try {
      const response = await chatAPI.send(userMsg.content);
      // response shape: {reply, providers?, agent_trace?, needs_clarification?}
      const botMsg: Message = {
        id: Date.now().toString(),
        role: 'bot',
        content: response.reply,
        providers: response.providers,
        trace: response.agent_trace,
        needsClarification: response.needs_clarification,
      };
      setMessages((prev) => [...prev.filter((m) => m.id !== 'typing'), botMsg]);
    } catch (e: any) {
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== 'typing'),
        {
          id: Date.now().toString(),
          role: 'bot',
          content: e.message || 'Kuch masla aa gaya. Dobara try karo.',
        }
      ]);
    } finally {
      setLoadingSend(false);
    }
  };

  const handleClearHistory = () => {
    if (Platform.OS === 'web') {
      if (window.confirm('Kya aap poori chat history delete karna chahte hain?')) {
        chatAPI.clearHistory().then(() => {
          setMessages([]);
          showWelcomeMessage();
        }).catch(() => alert('Error: Delete nahi hua'));
      }
    } else {
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
    }
  };

  const handleNewConversation = () => {
    if (Platform.OS === 'web') {
      if (window.confirm('Current chat screen clear ho jayegi. Naya Chat Shuru Karo?')) {
        setMessages([]);
        showWelcomeMessage();
      }
    } else {
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
            }
          }
        ]
      );
    }
  };

  const renderMessage = ({ item }: { item: Message }) => {
    if (item.role === 'user') {
      return (
        <View className="self-end max-w-[80%] mb-3 px-2">
          <View className="bg-gradient-to-r from-emerald-600 to-emerald-500 rounded-3xl rounded-br-md px-4 py-3 shadow-lg">
            <Text className="text-white text-base leading-5">{item.content}</Text>
          </View>
          <Text className="text-xs text-gray-500 mt-1 text-right">You</Text>
        </View>
      );
    }

    // Bot message
    if (item.content === '...') {
      // Typing indicator
      return (
        <View className="self-start max-w-[80%] mb-4 px-2">
          <View className="bg-gray-800 rounded-3xl rounded-bl-md px-4 py-3 flex-row items-center">
            <View className="flex-row space-x-1">
              <View className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              <View className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              <View className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            </View>
            <Text className="text-gray-400 ml-2 text-sm">Karoo soch raha hai...</Text>
          </View>
        </View>
      );
    }

    return (
      <View className="self-start max-w-[85%] mb-4 px-2">
        <View className="bg-gray-800 rounded-3xl rounded-bl-md px-4 py-3 shadow-lg border border-gray-700">
          <Text className="text-white text-base leading-6">{item.content}</Text>
        </View>
        <Text className="text-xs text-gray-500 mt-1">Karoo AI 🤖</Text>

        {/* Provider cards (if any) */}
        {item.providers && item.providers.length > 0 && (
          <View className="mt-3 space-y-2">
            <Text className="text-emerald-500 font-semibold text-sm mb-1">
              ✨ {item.providers.length} Provider{item.providers.length > 1 ? 's' : ''} Mil Gaye
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

        {/* Agent trace collapsible */}
        {item.trace && (
          <TraceCollapsible trace={item.trace} />
        )}
      </View>
    );
  };

  return (
    <View className="flex-1 bg-gray-950">
      {/* Header with gradient */}
      <View className="bg-gradient-to-r from-gray-900 to-gray-800 border-b border-emerald-500/20 shadow-lg">
        <View className="flex-row items-center justify-between px-4 py-4">
          <View>
            <Text className="text-2xl font-bold text-emerald-500">Karoo AI</Text>
            <Text className="text-xs text-gray-400 mt-0.5">Powered by Google Gemini 🤖</Text>
          </View>
          <View className="flex-row items-center gap-3">
            <TouchableOpacity
              onPress={handleClearHistory}
              className="p-2 bg-red-500/10 rounded-lg"
            >
              <Feather name="trash-2" size={18} color="#ef4444" />
            </TouchableOpacity>
            <TouchableOpacity
              onPress={handleNewConversation}
              className="p-2 bg-emerald-500/10 rounded-lg"
            >
              <Feather name="plus-circle" size={18} color="#10b981" />
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => router.push('/(user)/notifications')}
              className="relative"
            >
              <View className="p-2 bg-emerald-500/10 rounded-lg">
                <Feather name="bell" size={20} color="#10b981" />
              </View>
              {unreadCount > 0 && (
                <View className="absolute -right-1 -top-1 bg-red-500 rounded-full w-5 h-5 items-center justify-center border-2 border-gray-900">
                  <Text className="text-xs text-white font-bold">{unreadCount}</Text>
                </View>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {/* Message list */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        inverted={false}
        contentContainerStyle={{ padding: 12 }}
        showsVerticalScrollIndicator={false}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
      />

      {/* Input bar with gradient */}
      <View className="bg-gradient-to-t from-gray-900 to-gray-800 border-t border-emerald-500/20 shadow-2xl">
        <View className="flex-row items-center px-4 py-3 gap-2">
          <TextInput
            placeholder="Urdu ya English mein likhein..."
            placeholderTextColor="#6b7280"
            className="flex-1 bg-gray-800 rounded-2xl px-4 py-3 text-white text-base border border-gray-700 focus:border-emerald-500"
            value={input}
            onChangeText={setInput}
            onSubmitEditing={handleSend}
            multiline
            maxLength={500}
          />
          <TouchableOpacity
            className={`p-3 rounded-2xl ${loadingSend ? 'bg-gray-700' : 'bg-gradient-to-r from-emerald-600 to-emerald-500'} shadow-lg`}
            onPress={handleSend}
            disabled={loadingSend || !input.trim()}
          >
            {loadingSend ? (
              <ActivityIndicator color="#fff" size="small" />
            ) : (
              <Feather name="send" size={22} color="#fff" />
            )}
          </TouchableOpacity>
        </View>
        <Text className="text-xs text-gray-500 text-center pb-2">
          Powered by Google Gemini • Multilingual AI
        </Text>
      </View>
    </View>
  );
}

// ---------- Trace Collapsible Component ----------
function TraceCollapsible({ trace }: { trace: string }) {
  const [expanded, setExpanded] = useState(false);
  const toggle = () => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpanded(!expanded);
  };
  return (
    <View className="mt-2">
      <TouchableWithoutFeedback onPress={toggle}>
        <View className="flex-row items-center">
          <Feather name="search" size={16} color="#10b981" />
          <Text className="ml-1 text-emerald-500">🔍 AI Reasoning dekho</Text>
        </View>
      </TouchableWithoutFeedback>
      {expanded && (
        <ScrollView className="bg-gray-800 rounded-md p-2 mt-1 max-h-40">
          <Text className="text-xs font-mono text-white">{trace}</Text>
        </ScrollView>
      )}
    </View>
  );
}
