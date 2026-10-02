import { Row, Col, Input } from 'antd';
import { useState, useEffect, useImperativeHandle } from 'react';

interface DirPickerProps {
	onError?: (error: Error) => void;
	onSuccess?: (dir: string) => void;
	ref?: React.Ref<{ updateDir: () => void }>;
}

export default function DirPicker(props: DirPickerProps) {
	const [dir, setPath] = useState<string>();
	useImperativeHandle(
		props.ref,
		() => ({
			updateDir: () => {
				getOutDir();
			}
		}),
		[]
	);
	const handleChooseOutdir = async () => {
		try {
			const dir = await window.pywebview?.api?.select_dir(true);
			if (dir) {
				setPath(dir);
				props.onSuccess?.(dir);
			}
		} catch (e) {
			props.onError?.(e instanceof Error ? e : new Error(String(e)));
		}
	};
	const getOutDir = async () => {
		const dir = await window.pywebview?.api?.get_output_dir().catch(e => {
			props.onError?.(e);
		});
		if (dir) setPath(dir!);
	};
	useEffect(() => {
		getOutDir();
	}, []);

	return (
		<Row gutter={4} align="middle" wrap={false}>
			<Col flex={1}>dir:</Col>
			<Col flex={5}>
				{/* <Tooltip placement="leftTop" title={dir}> */}
				<Input.TextArea
					autoSize={{
						maxRows: 3
					}}
					onClick={handleChooseOutdir}
					value={dir || 'Same as the file by default'}
					readOnly
				/>
				{/* </Tooltip> */}
			</Col>
			<Col flex={1}></Col>
		</Row>
	);
}
