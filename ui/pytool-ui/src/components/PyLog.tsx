import { useEffect, useReducer } from 'react';
import { Listy, Button, Row, Col, Badge } from 'antd';
import { ExportOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

type Item = {
	id: string;
	content?: string;
	path?: string;
	timestamp: string;
	icon: 'success' | 'error' | 'processing' | 'default' | 'warning';
};
type Action = {
	type: 'new' | 'clear';
} & Item;
const reducer = (state: Item[], action: Action) => {
	switch (action.type) {
		case 'new':
			return [
				...state,
				{
					...action,
					icon: action.icon ? action.icon : 'processing',
					id: action.id || Math.random().toString(36).substring(2, 9),
					timestamp: dayjs().format('HH:mm:ss')
				}
			];

		case 'clear':
			return [];
		default:
			return state;
	}
};

export default function PyLog() {
	const [logs, dispatch] = useReducer<Item[], [Action]>(reducer, [
		{
			content: 'Application ui loaded',
			timestamp: dayjs().format('HH:mm'),
			icon: 'success',
			id: Math.random().toString(36).substring(2, 9)
			// path: '~'
		}
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
				<Row
					align="top"
					// className="w-full"
				>
					<Col flex="auto">
						<Badge
							status={item.icon}
							text={
								<span className="text-gray-500">{`${item.timestamp} - ${item.content}`}</span>
							}
						></Badge>
					</Col>
					<Col span={4}>
						{item.path && (
							<Button
								type="link"
								size="small"
								onClick={() => handleOpen(item.path!)}
							>
								<ExportOutlined />
							</Button>
						)}
					</Col>
				</Row>
				// <Alert
				// 	title={`log`}
				// 	description={`${item.timestamp} - ${item.content}`}
				// 	type={item.icon}
				// 	showIcon={!!item.icon}
				// 	action={

				// 	}
				// />
			)}
			virtual
			items={logs}
			height={400}
			rowKey="id"
		/>
	);
}

