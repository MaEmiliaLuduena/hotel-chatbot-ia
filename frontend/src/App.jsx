import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Image, Calendar, Users, Mail, Phone, User } from 'lucide-react'; // íconos

const HotelChatbot = () => {
  // El primer mensaje es un assistant de bienvenida
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '¡Bienvenido al Gran Hotel Bell Ville! 🏨 Soy BellBot, tu asistente virtual. ¿En qué puedo ayudarte hoy? Puedo ayudarte a reservar una habitación, mostrarte nuestras opciones o responder cualquier pregunta sobre el hotel.',
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [showReservationForm, setShowReservationForm] = useState(false);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Para el formulario de reserva
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    telefono: '',
    tipo_habitacion: '',
    fecha_checkin: '',
    fecha_checkout: '',
    huespedes: 1
  });

  // Descripción de las habitaciones
  const habitaciones = {
    matrimonial: { nombre: 'Matrimonial', capacidad: 2 },
    doble: { nombre: 'Doble', capacidad: 2 },
    triple_matrimonial: { nombre: 'Triple (1 Matrimonial + 1 Simple)', capacidad: 3 },
    triple_individual: { nombre: 'Triple (3 Individuales)', capacidad: 3 }
  };

  // Envía imagenes de habitaciones segun corresponda
  const imagenesHabitaciones = {
    matrimonial: 'https://images.unsplash.com/photo-1645619200527-c6786729c2da?w=870',
    doble: 'https://images.unsplash.com/photo-1605346576608-92f1346b67d6?w=870',
    triple_matrimonial: 'https://images.unsplash.com/photo-1648383228240-6ed939727ad6?w=774',
    triple_individual: 'https://images.unsplash.com/photo-1737517302831-e7b8a8eaa97c?w=870'
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Web Speech API - Inicializa reconocimiento de voz
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'es-AR';

      // cuando el usuario habla, el evento onresult captura el texto y lo envía al backend igual que si lo hubiera escrito.
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = () => {
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Inicia/detiene la escucha
  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      recognitionRef.current?.start();
      setIsListening(true);
    }
  };

  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // El frontend hace llamadas HTTP al backend usando fetch. Por ejemplo, cuando el usuario envía un mensaje.
    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          history: messages
        })
      });

      const data = await response.json();

      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        imagenes: data.imagenes || [],
        timestamp: data.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);

      // SÍNTESIS DE VOZ DESACTIVADA
      // if ('speechSynthesis' in window) {
      //   const utterance = new SpeechSynthesisUtterance(data.response);
      //   utterance.lang = 'es-AR';
      //   utterance.rate = 0.9;
      //   window.speechSynthesis.speak(utterance);
      // }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: 'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta nuevamente.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };

  const handleReservationSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/reservar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (data.success) {
        const confirmationMessage = {
          role: 'assistant',
          content: `¡Reserva confirmada exitosamente! 🎉\n\nID de Reserva: ${data.reserva_id}\nNoches: ${data.noches}\nPrecio Total: $${data.precio_total.toLocaleString('es-AR')}\n\nRecibirás un email de confirmación en ${formData.email}. ¡Esperamos tu visita!`,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, confirmationMessage]);
        setShowReservationForm(false);
        setFormData({
          nombre: '',
          email: '',
          telefono: '',
          tipo_habitacion: '',
          fecha_checkin: '',
          fecha_checkout: '',
          huespedes: 1
        });
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: 'Hubo un error al procesar tu reserva. Por favor, intenta nuevamente o contacta a recepción.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Botones-Acciones rápidas del Chatbot
  const quickActions = [
    { text: 'Ver habitaciones disponibles', icon: Image },
    { text: 'Consultar precios', icon: Calendar },
    { text: 'Hacer una reserva', icon: Users },
    { text: 'Servicios del hotel', icon: Mail }
  ];

  return (
    // Frontend - Diseño visual de chatbot
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-6 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">Gran Hotel Bell Ville</h1>
          <p className="text-blue-100">Bell Ville, Córdoba, Argentina 🇦🇷</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl p-4 shadow-md ${
                message.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-br-none' 
                  : 'bg-white text-gray-800 rounded-bl-none'
              }`}>
                <p className="whitespace-pre-wrap">{message.content}</p>
                
                {message.imagenes && message.imagenes.length > 0 && (
                  <div className="mt-4 grid grid-cols-1 gap-3">
                    {message.imagenes.map((tipo, imgIndex) => (
                      <div key={imgIndex} className="bg-gray-50 rounded-lg overflow-hidden">
                        <img 
                          src={imagenesHabitaciones[tipo]} 
                          alt={habitaciones[tipo]?.nombre}
                          className="w-full h-48 object-cover"
                        />
                        <div className="p-3">
                          <h3 className="font-semibold text-gray-800">
                            {habitaciones[tipo]?.nombre}
                          </h3>
                          <p className="text-sm text-gray-600">
                            Capacidad: {habitaciones[tipo]?.capacidad} personas
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                <p className="text-xs mt-2 opacity-70">
                  {new Date(message.timestamp).toLocaleTimeString('es-AR', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white rounded-2xl rounded-bl-none p-4 shadow-md">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {!showReservationForm && (
        <div className="px-4 pb-2">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-2 overflow-x-auto pb-2">
              {quickActions.map((action, index) => {
                const Icon = action.icon;
                return (
                  <button
                    key={index}
                    onClick={() => sendMessage(action.text)}
                    className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-blue-50 text-gray-700 rounded-full shadow-sm whitespace-nowrap transition-colors"
                  >
                    <Icon size={16} />
                    <span className="text-sm">{action.text}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Calendario de reservas */}
      {showReservationForm && (
        <div className="px-4 pb-4">
          <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Completar Reserva</h3>
            <form onSubmit={handleReservationSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <User size={16} className="inline mr-1" /> Nombre Completo
                </label>
                <input
                  type="text"
                  required
                  value={formData.nombre}
                  onChange={(e) => setFormData({...formData, nombre: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Mail size={16} className="inline mr-1" /> Email
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Phone size={16} className="inline mr-1" /> Teléfono
                </label>
                <input
                  type="tel"
                  required
                  value={formData.telefono}
                  onChange={(e) => setFormData({...formData, telefono: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Image size={16} className="inline mr-1" /> Tipo de Habitación
                </label>
                <select
                  required
                  value={formData.tipo_habitacion}
                  onChange={(e) => setFormData({...formData, tipo_habitacion: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Seleccionar...</option>
                  {Object.entries(habitaciones).map(([key, hab]) => (
                    <option key={key} value={key}>{hab.nombre}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Calendar size={16} className="inline mr-1" /> Check-in
                </label>
                <input
                  type="date"
                  required
                  value={formData.fecha_checkin}
                  onChange={(e) => setFormData({...formData, fecha_checkin: e.target.value})}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Calendar size={16} className="inline mr-1" /> Check-out
                </label>
                <input
                  type="date"
                  required
                  value={formData.fecha_checkout}
                  onChange={(e) => setFormData({...formData, fecha_checkout: e.target.value})}
                  min={formData.fecha_checkin || new Date().toISOString().split('T')[0]}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Users size={16} className="inline mr-1" /> Número de Huéspedes
                </label>
                <input
                  type="number"
                  required
                  min="1"
                  max="3"
                  value={formData.huespedes}
                  onChange={(e) => setFormData({...formData, huespedes: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div className="md:col-span-2 flex gap-3">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold transition-colors"
                >
                  {isLoading ? 'Procesando...' : 'Confirmar Reserva'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowReservationForm(false)}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="p-4 bg-white border-t">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <button
              type="button"
              onClick={toggleListening}
              className={`p-3 rounded-full transition-colors ${
                isListening 
                  ? 'bg-red-500 text-white animate-pulse' 
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
              }`}
            >
              {isListening ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
            
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Escribe tu mensaje o usa el micrófono..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send size={20} />
            </button>
            
            <button
              type="button"
              onClick={() => setShowReservationForm(!showReservationForm)}
              className="px-4 py-3 bg-green-600 text-white rounded-full hover:bg-green-700 transition-colors"
            >
              <Calendar size={20} />
            </button>
          </form>
          
          <p className="text-xs text-gray-500 text-center mt-2">
            Presiona el micrófono para hablar o escribe tu mensaje
          </p>
        </div>
      </div>
    </div>
  );
};

export default HotelChatbot;