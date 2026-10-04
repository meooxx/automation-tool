import { Button, Col, Row, Typography, Badge } from 'antd';
import { ExportOutlined } from '@ant-design/icons';
import { useEffect, useState, startTransition, ViewTransition } from 'react';

const MAX_SHOW_COUNT = 5;

export default function LogDir() {
	const [logPath, setLogPath] = useState<string>();
	const [showCount, setShow] = useState<number>(0);
	const handleClick = () => {
		startTransition(() => {
			setShow(pre => (pre <= MAX_SHOW_COUNT ? pre + 1 : 0));
		});
	};
	useEffect(() => {
		if (showCount <= MAX_SHOW_COUNT) return;
		window.pywebview?.api?.get_log_path().then(path => {
			if (path) setLogPath(path);
		});
	}, [showCount]);
	if (showCount <= MAX_SHOW_COUNT) {
		return (
			<ViewTransition default="none" exit="auto">
				<Row justify="start">
					<Col offset={1}>
						<Badge onClick={handleClick} status="processing" text="Running" />
					</Col>
				</Row>
			</ViewTransition>
		);
	}

	return (
		<ViewTransition default="none" enter="auto">
			<Row gutter={4} align="middle" wrap={false} style={{ marginTop: 8 }}>
				<Col flex="1">Log:</Col>
				<Col flex="5" style={{ minWidth: 0, overflow: 'hidden' }}>
					<Typography.Text
						type="secondary"
						ellipsis={{ tooltip: logPath }}
						// copyable={{ text: logPath }}
					>
						{logPath}
					</Typography.Text>
				</Col>
				<Col flex="1">
					<Button
						type="link"
						size="small"
						icon={<ExportOutlined />}
						aria-label="Open error log"
						disabled={!logPath}
						onClick={() => {
							if (logPath) window.pywebview?.api?.open_path(logPath);
						}}
					/>
				</Col>
			</Row>
		</ViewTransition>
	);
}

