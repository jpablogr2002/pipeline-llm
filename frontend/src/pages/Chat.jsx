import React, { useState } from 'react';
import api from '../api';
import { Send, Bot, User, Loader2, CheckCircle2 } from 'lucide-react';

const Chat = () => {
  const [messages, setMessages] = useState([
    { role: 'agent', text: 'Hola, soy el agente de MediaGroup. Pega un artículo y presiona enviar.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Estado para la trazabilidad (Panel ReAct)
  const [trace, setTrace] = useState([
    { state: 'Reason', message: 'Esperando entrada del usuario...' }
  ]);

  const addTrace = (state, message) => {
    setTrace(prev => [...prev, { state, message }]);
  };

  const pollResult = async (taskId) => {
    try {
      const response = await api.get(`/webhook/result/${taskId}`);
      
      if (response.data.status === 'processing') {
        // Si sigue procesando, esperamos 2 segundos y volvemos a preguntar
        setTimeout(() => pollResult(taskId), 2000);
      } else if (response.data.status === 'completed') {
        // ¡El agente terminó!
        addTrace('Observe', 'Análisis completado por Vertex AI.');
        
        // Formateamos la respuesta para que se vea bien
        setMessages(prev => [...prev, { 
          role: 'agent', 
          text: `Análisis finalizado (Latencia: ${response.data.latency_ms}ms):\n\n${response.data.result}` 
        }]);
        setLoading(false);
      } else {
        throw new Error("Error en el procesamiento");
      }
    } catch (error) {
      addTrace('Error', 'Falló la consulta del resultado.');
      setMessages(prev => [...prev, { role: 'agent', text: '❌ Hubo un error al procesar el artículo.' }]);
      setLoading(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    
    const currentInput = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: currentInput }]);
    setLoading(true);
    
    // Reiniciamos la trazabilidad
    setTrace([{ state: 'Reason', message: 'El agente recibió el artículo y decidió analizarlo.' }]);

    try {
      // 1. Enviamos al webhook
      const response = await api.post('/webhook/ingest', {
        title: "Artículo desde el Chat",
        content: currentInput,
        source_url: "https://chat.local"
      });

      const taskId = response.data.task_id;
      addTrace('Act', 'Invocando Tool: analizar_con_llm() en segundo plano...');
      
      // 2. Empezamos a preguntar por el resultado
      pollResult(taskId);

    } catch (err) {
      addTrace('Error', 'No se pudo conectar con el backend.');
      setMessages(prev => [...prev, { role: 'agent', text: 'Error de conexión con el servidor.' }]);
      setLoading(false);
    }
  };

  const getTraceColor = (state) => {
    switch(state) {
      case 'Reason': return 'bg-brand-pale text-brand-dark';
      case 'Act': return 'bg-brand-light text-brand-dark';
      case 'Observe': return 'bg-green-100 text-green-700';
      case 'Error': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100';
    }
  };

  return (
    <div className="flex h-full p-8 gap-6">
      {/* Panel de Chat */}
      <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col overflow-hidden">
        <div className="bg-brand-pale p-4 border-b border-brand-light">
          <h2 className="text-lg font-bold text-brand-dark flex items-center">
            <Bot className="mr-2" /> Asistente ADK
          </h2>
        </div>
        
        <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-gray-50">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-4 rounded-xl flex items-start gap-3 ${
                msg.role === 'user' 
                  ? 'bg-brand-blue text-white rounded-br-none' 
                  : 'bg-white text-gray-800 border border-gray-100 shadow-sm rounded-bl-none'
              }`}>
                {msg.role === 'agent' && <Bot size={20} className="mt-1 text-brand-cyan shrink-0" />}
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                {msg.role === 'user' && <User size={20} className="mt-1 text-brand-light shrink-0 ml-2" />}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white p-3 rounded-xl border border-gray-100 shadow-sm flex items-center gap-2 text-gray-500">
                <Loader2 className="animate-spin" size={18} /> El agente está pensando...
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleSend} className="p-4 bg-white border-t border-gray-100 flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Pega el texto del artículo aquí..."
            disabled={loading}
            className="flex-1 border border-gray-200 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-brand-cyan text-sm disabled:bg-gray-100"
          />
          <button 
            type="submit" 
            disabled={loading}
            className="bg-brand-cyan hover:bg-brand-blue text-white p-3 rounded-lg transition-colors disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </form>
      </div>

      {/* Panel de Razonamiento (ReAct) */}
      <div className="w-80 bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col">
        <h3 className="text-md font-bold text-brand-dark mb-4 pb-2 border-b border-gray-100">Trazabilidad (ReAct)</h3>
        <div className="space-y-4 flex-1 overflow-y-auto text-sm">
          {trace.map((t, i) => (
            <div key={i} className="flex gap-3">
              <div className="mt-1">
                <span className={`flex h-6 w-6 items-center justify-center rounded-full font-bold text-xs ${getTraceColor(t.state)}`}>
                  {t.state.charAt(0)}
                </span>
              </div>
              <div>
                <p className="font-semibold text-gray-800">{t.state}</p>
                <p className="text-gray-500 text-xs mt-1">{t.message}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Chat;