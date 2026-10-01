import { useEffect, useReducer } from 'react';
import { Listy, Alert, Button } from 'antd';
import dayjs from 'dayjs';

type Item = {
	id: string;
	content?: string;
	path?: string;
	timestamp: string;
	icon: 'success' | 'error' | 'info';
};
type Action = {
	type: 'new' | 'clear';
} & Item;
const reducer = (state: Item[], action: Action) => {
	switch (action.type) {
		case 'new':
			return [
				{
					...action,
					icon: action.icon ? action.icon : 'info',
					id: action.id || Math.random().toString(36).substring(2, 9),
					timestamp: dayjs().format('HH:mm:ss')
				},
				...state
			];

		case 'clear':
			return [];
		default:
			return state;
	}
};

export default function PyLog() {
	const [logs, dispatch] = useReducer<Item[], [Action]>(reducer, [
		// {
		// 	content: 'output dir: /output',
		// 	timestamp: dayjs().format('HH:mm:ss'),
		// 	icon: 'success',
		// 	id: Math.random().toString(36).substring(2, 9),
		// 	path: '~'
		// }
	]);
	const handleOpen = (path: string) => {
		window.pywebview?.api?.open_dir(path);
	};
	useEffect(() => {
		const sendMessage = (action: Omit<Action, 'id'> & { id?: string }) => {
			action.id = Math.random().toString(36).substring(2, 9);
			dispatch(action as Action);
		};
		if (!window['CALL_METHODS']) {
			window['CALL_METHODS'] = new Map();
		}
		window['CALL_METHODS'].set('push_log', sendMessage);
		return () => {
			window['CALL_METHODS']?.delete('push_log');
		};
	}, [dispatch]);
	return (
		<Listy<Item>
			itemRender={item => (
				<Alert
					title={`log - ${item.timestamp}`}
					description={item.content}
					type={item.icon}
					showIcon={!!item.icon}
					action={
						item.path ? (
							<Button onClick={() => handleOpen(item.path!)} type="primary">
								open
							</Button>
						) : null
					}
				/>
			)}
			virtual
			items={logs}
			height={400}
			rowKey="id"
		/>
	);
}

