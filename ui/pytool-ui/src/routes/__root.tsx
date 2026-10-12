import { HeadContent, Scripts, createRootRoute } from '@tanstack/react-router';
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools';
import { TanStackDevtools } from '@tanstack/react-devtools';
import appCss from '../styles.css?url';
import { useEffect } from 'react';

export const Route = createRootRoute({
	head: () => ({
		meta: [
			{
				charSet: 'utf-8'
			},
			{
				name: 'viewport',
				content: 'width=device-width, initial-scale=1'
			},
			{
				title: 'pytool-ui'
			}
		],
		links: [
			{
				rel: 'stylesheet',
				href: appCss
			}
		]
	}),
	shellComponent: RootDocument
});

function RootDocument({ children }: { children: React.ReactNode }) {
	useEffect(() => {
		const signalReady = () => {
			window.pywebview?.api?.ready();
		};
		// API may already be present (macOS), or arrive later (Windows WebView2).
		if (window.pywebview?.api) {
			signalReady();
		}
		window.addEventListener('pywebviewready', signalReady);
		return () => {
			window.removeEventListener('pywebviewready', signalReady);
		};
	}, []);
	return (
		<html lang="en">
			<head>
				<HeadContent />
			</head>
			<body>
				{children}
				<TanStackDevtools
					config={{
						position: 'bottom-right'
					}}
					plugins={[
						{
							name: 'Tanstack Router',
							render: <TanStackRouterDevtoolsPanel />
						}
					]}
				/>
				<Scripts />
			</body>
		</html>
	);
}

