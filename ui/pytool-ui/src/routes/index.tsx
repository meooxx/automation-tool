import { createFileRoute } from '@tanstack/react-router';
import { Row, Col, message, DatePicker, Space, ColorPicker } from 'antd';
import PyUpload from '../components/PyUpload';

export const Route = createFileRoute('/')({ component: Home });

declare global {
	interface Window {
		pywebview?: {
			api?: {
				bind_drop_event: (selector: string) => Promise<boolean>;
				unbind_drop_event: (selector: string) => Promise<boolean>;
				select_file: () => Promise<string | null>;
			};
		};
	}
}

function Home() {
	const [messageApi, contextHolder] = message.useMessage();
	const handleUploadSuccess = (filePath: string): void => {
		messageApi.success(`Choosed: ${filePath}`);
	};
	return (
		<>
			{contextHolder}
			<div>
				{contextHolder}
				<Row gutter={8}>
					<Col sm={12} lg={8}>
						<Space vertical style={{ width: '100%' }}>
							<PyUpload onSuccess={handleUploadSuccess}></PyUpload>
							<DatePicker style={{ width: '100%' }} picker="month" />
						</Space>
					</Col>
					<Col sm={12} lg={8}></Col>
					<Col sm={12} lg={8}></Col>
				</Row>
			</div>
		</>
	);
}

