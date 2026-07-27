import { apiFetch } from './client.js';

export function sendAgentMessage({ message, thread_id, user_id }) {
	return apiFetch('/agent/re_agent', {
		method: 'POST',
		body: { message, thread_id: thread_id ?? null, user_id }
	});
}

export function getMessages(threadId) {
	return apiFetch('/agent/get_message', { params: { thread_id: threadId } });
}

export function getThreads(userId) {
	return apiFetch('/agent/get_chat', { params: { user_id: userId } });
}
